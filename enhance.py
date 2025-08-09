#!/usr/bin/env python
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.misc
import math
from PIL import Image
import random
from utils import *
from models.models import *

def process_image(deg_image_path, save_path, generator, task):
    """
    Processes a single image: loads, pads, enhances, and saves it.
    """
    try:
        print(f"Processing {deg_image_path}...")
        deg_image = Image.open(deg_image_path)
        deg_image = deg_image.convert('L')
        
        temp_image_path = 'curr_image.png'
        deg_image.save(temp_image_path)
        test_image = plt.imread(temp_image_path)

        h = ((test_image.shape[0] // 256) + 1) * 256
        w = ((test_image.shape[1] // 256) + 1) * 256

        test_padding = np.zeros((h, w)) + 1
        test_padding[:test_image.shape[0], :test_image.shape[1]] = test_image

        test_image_p = split2(test_padding.reshape(1, h, w, 1), 1, h, w)
        predicted_list = []
        for l in range(test_image_p.shape[0]):
            predicted_list.append(generator.predict(test_image_p[l].reshape(1, 256, 256, 1)))

        predicted_image = np.array(predicted_list)
        predicted_image = merge_image2(predicted_image, h, w)

        predicted_image = predicted_image[:test_image.shape[0], :test_image.shape[1]]
        predicted_image = predicted_image.reshape(predicted_image.shape[0], predicted_image.shape[1])

        if task == 'binarize':
            bin_thresh = 0.95
            predicted_image = (predicted_image[:, :] > bin_thresh) * 1

        result_image = Image.fromarray((predicted_image * 255).astype(np.uint8), mode='L')
        result_image.save(save_path, quality=95)
        print(f"Successfully saved result to {save_path}")

    except Exception as e:
        print(f"Failed to process {deg_image_path}. Error: {e}")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python enhance.py <task> <input_path> <output_path>")
        print("Tasks: binarize, deblur, unwatermark")
        print("<input_path> can be a single image file or a directory of images.")
        print("<output_path> must be a file path if input is a file, or a directory path if input is a directory.")
        sys.exit(1)

    task = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3]

    # Load the appropriate model
    generator = None
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
        print("Wrong task, please specify a correct task (binarize, deblur, unwatermark)!")
        sys.exit(1)

    # Check if input is a directory or a single file
    if os.path.isdir(input_path):
        # Bulk processing
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print(f"Created output directory: {output_path}")

        image_files = [f for f in os.listdir(input_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        print(f"Found {len(image_files)} images in {input_path}")

        for filename in image_files:
            deg_image_path = os.path.join(input_path, filename)
            # Preserve the original filename in the output directory
            save_path = os.path.join(output_path, filename)
            process_image(deg_image_path, save_path, generator, task)
        
        # Clean up the temporary file
        if os.path.exists('curr_image.png'):
            os.remove('curr_image.png')

    elif os.path.isfile(input_path):
        # Single file processing
        process_image(input_path, output_path, generator, task)
        # Clean up the temporary file
        if os.path.exists('curr_image.png'):
            os.remove('curr_image.png')
    else:
        print(f"Error: Input path not found or is not a valid file/directory: {input_path}")
        sys.exit(1)