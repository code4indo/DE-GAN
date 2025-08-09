## Untuk Memulai Restorasi Dokumen Ikuti Langkah Ini:

1.  **Menyiapkan Virtual Environment**
    1.  Membuat virtual environment:
        ```bash
        python3 -m venv .venv
        ```
    2.  Aktifkan virtual environment: lokasi virtual env ada di /TESIS/DE-GAN
        ```bash
        source .venv/bin/activate
        ```

2.  **Install Library yang Dibutuhkan**
    ```bash
    pip install -r requirement
    ```

3.  **Pastikan Model Sudah di Load ke Direktori `weights`**

4.  **Siapkan Gambar Input pada Folder `images`**

5.  **Jalankan Perintah untuk berbagai jenis kerusakan**

**Binarisasi**
```bash
python3 enhance.py binarize ./images/tiga.jpg ./results/tiga.png
```

**Deblur**
```bash
python3 enhance.py deblur ./images/tiga.jpg ./results/tiga.png
```

**enhance**
```bash
python3 enhance.py unwatermark ./images/tiga.jpg ./results/tiga.png
```

Hasil restorasi ada pada folder `results`.