#!/usr/bin/env python
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import math
from PIL import Image
import random
import time
import json
import datetime
import platform
from utils import *
from models.models import *

def process_image(deg_image_path, save_path, generator, task):
    """
    Processes a single image and returns a report dictionary.
    """
    start_time = time.time()
    report = {
        "input_file": deg_image_path,
        "output_file": save_path,
        "status": "Pending",
        "processing_time_seconds": -1,
        "error_message": None,
        "original_dimensions": None,
        "padded_dimensions": None
    }

    try:
        deg_image = Image.open(deg_image_path)
        deg_image = deg_image.convert('L')
        
        temp_image_path = 'curr_image.png'
        deg_image.save(temp_image_path)
        test_image = plt.imread(temp_image_path)
        report["original_dimensions"] = f"{test_image.shape[1]}x{test_image.shape[0]}"

        h = ((test_image.shape[0] // 256) + 1) * 256
        w = ((test_image.shape[1] // 256) + 1) * 256
        report["padded_dimensions"] = f"{w}x{h}"

        test_padding = np.zeros((h, w)) + 1
        test_padding[:test_image.shape[0], :test_image.shape[1]] = test_image

        test_image_p = split2(test_padding.reshape(1, h, w, 1), 1, h, w)
        predicted_list = []
        for l in range(test_image_p.shape[0]):
            predicted_list.append(generator.predict(test_image_p[l].reshape(1, 256, 256, 1), verbose=0))

        predicted_image = np.array(predicted_list)
        predicted_image = merge_image2(predicted_image, h, w)

        predicted_image = predicted_image[:test_image.shape[0], :test_image.shape[1]]
        predicted_image = predicted_image.reshape(predicted_image.shape[0], predicted_image.shape[1])

        if task == 'binarize':
            bin_thresh = 0.95
            predicted_image = (predicted_image[:, :] > bin_thresh) * 1

        result_image = Image.fromarray((predicted_image * 255).astype(np.uint8), mode='L')
        result_image.save(save_path, quality=95)
        
        report["status"] = "Success"

    except Exception as e:
        report["status"] = "Failed"
        report["error_message"] = str(e)
    
    end_time = time.time()
    report["processing_time_seconds"] = round(end_time - start_time, 2)
    return report


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python enhance.py <task> <input_path> <output_path>")
        print("Tasks: binarize, deblur, unwatermark")
        print("<input_path> can be a single image file or a directory of images.")
        print("<output_path> must be a file path if input is a file, or a directory path if input is a directory.")
        sys.exit(1)

    # --- Initialize Report ---
    main_report = {
        "report_generated_at": datetime.datetime.now().isoformat(),
        "execution_summary": {},
        "environment_info": {},
        "image_details": []
    }

    # --- Gather Environment Info ---
    try:
        import tensorflow as tf
        main_report["environment_info"]["python_version"] = platform.python_version()
        main_report["environment_info"]["tensorflow_version"] = tf.__version__
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            main_report["environment_info"]["gpu_detected"] = True
            main_report["environment_info"]["gpu_details"] = [gpu.name for gpu in gpus]
            print(f"-> Ditemukan {len(gpus)} GPU. Proses akan menggunakan: {gpus[0].name}")
        else:
            main_report["environment_info"]["gpu_detected"] = False
            print("-> Tidak ada GPU yang terdeteksi, proses akan berjalan menggunakan CPU.")
    except ImportError:
        main_report["environment_info"]["gpu_detected"] = False
        main_report["environment_info"]["tensorflow_version"] = "Not Found"
        print("-> TensorFlow tidak terinstall, proses akan berjalan menggunakan CPU.")

    task = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3]

    main_report["execution_summary"] = {
        "task": task,
        "input_path": input_path,
        "output_path": output_path
    }

    # --- Load Model ---
    generator = None
    try:
        if task == 'binarize':
            generator = generator_model(biggest_layer=1024)
            generator.load_weights("weights/binarization_generator_weights.h5")
        elif task == 'deblur':
            generator = generator_model(biggest_layer=1024)
            generator.load_weights("weights/deblur_weights.h5")
        elif task == 'unwatermark':
            generator = generator_model(biggest_layer=512)
            generator.load_weights("weights/watermark_rem_weights.h5")
        else:
            print(f"Wrong task: {task}. Please specify a correct task (binarize, deblur, unwatermark)!")
            sys.exit(1)
    except Exception as e:
        print(f"Error loading model weights for task '{task}': {e}")
        sys.exit(1)

    # --- Process Images ---
    total_start_time = time.time()
    
    if os.path.isdir(input_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print(f"Created output directory: {output_path}")

        image_files = [f for f in os.listdir(input_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        print(f"Found {len(image_files)} images in {input_path}")

        for filename in image_files:
            deg_image_path = os.path.join(input_path, filename)
            save_path = os.path.join(output_path, filename)
            image_report = process_image(deg_image_path, save_path, generator, task)
            main_report["image_details"].append(image_report)
            print(f"  - Processed {filename}: {image_report['status']} in {image_report['processing_time_seconds']}s")
        
    elif os.path.isfile(input_path):
        image_report = process_image(input_path, output_path, generator, task)
        main_report["image_details"].append(image_report)
        print(f"  - Processed {os.path.basename(input_path)}: {image_report['status']} in {image_report['processing_time_seconds']}s")

    else:
        print(f"Error: Input path not found or is not a valid file/directory: {input_path}")
        sys.exit(1)

    # --- Finalize and Save Report ---
    total_end_time = time.time()
    
    success_count = sum(1 for r in main_report["image_details"] if r["status"] == "Success")
    failed_count = sum(1 for r in main_report["image_details"] if r["status"] == "Failed")
    
    summary = main_report["execution_summary"]
    summary["total_images_processed"] = len(main_report["image_details"])
    summary["total_success"] = success_count
    summary["total_failed"] = failed_count
    summary["total_processing_time_seconds"] = round(total_end_time - total_start_time, 2)
    summary["overall_status"] = "Completed" if failed_count == 0 else "Completed with errors"

    # Determine report path
    if os.path.isdir(output_path):
        report_path = os.path.join(output_path, f"report-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    else:
        report_dir = os.path.dirname(output_path)
        if not os.path.exists(report_dir) and report_dir != '':
            os.makedirs(report_dir)
        report_path = os.path.splitext(output_path)[0] + "_report.json"

    try:
        with open(report_path, 'w') as f:
            json.dump(main_report, f, indent=4)
        print(f"\nProcessing complete. Report saved to {report_path}")
    except Exception as e:
        print(f"\nError saving report file: {e}")

    # Clean up the temporary file
    if os.path.exists('curr_image.png'):
        os.remove('curr_image.png')
