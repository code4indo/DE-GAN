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
    pip install -r requirements.txt
    ```

3.  **Pastikan Model Sudah di Load ke Direktori `weights`**

4.  **Siapkan Gambar Input pada Folder `images` atau folder lainnya**

5.  **Jalankan Perintah Peningkatan Kualitas Gambar**

Skrip `enhance.py` dapat digunakan untuk tiga tugas: `binarize`, `deblur`, dan `unwatermark`. Skrip ini dapat memproses satu file gambar atau seluruh direktori berisi gambar.

### Penggunaan Dasar

Struktur perintahnya adalah:
```bash
python3 enhance.py <tugas> <path_input> <path_output>
```

### Contoh Penggunaan

**1. Memproses Satu File Gambar**

Untuk melakukan binarisasi pada satu gambar:
```bash
python3 enhance.py binarize ./images/nama_file_input.jpg ./results/nama_file_output.png
```
- Ganti `binarize` dengan `deblur` atau `unwatermark` sesuai kebutuhan.
- Ganti path input dan output sesuai dengan lokasi file Anda.

**2. Memproses Seluruh Direktori Gambar (Bulk Processing)**

Untuk melakukan binarisasi pada semua gambar dalam sebuah direktori:
```bash
python3 enhance.py binarize ./images/rusak/ ./results/rusak_hasil/
```
- Skrip akan memproses semua gambar (seperti .png, .jpg, .bmp) yang ada di direktori input (`./images/rusak/`).
- Direktori output (`./results/rusak_hasil/`) akan dibuat jika belum ada.
- Nama file di direktori output akan sama dengan nama file aslinya.


Hasil restorasi akan tersimpan di folder `results` atau direktori output yang Anda tentukan.