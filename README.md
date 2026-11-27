
# EDS DATA LAKE E-COMMERCE

Implementasi Rancangan Arsitektur Data Lake End-to-End
pada Industri E-Commerce Menggunakan Python, DuckDB,
dan Apache Parquet.

## Identitas

Nama: Hermina Maria Magdalena Karunumu
NIM: 24.K1.0060

## 1. Teknologi

- Python
- Pandas
- DuckDB
- Apache Parquet
- Visual Studio Code
- PowerShell

## 2. Dataset

Brazilian E-Commerce Public Dataset by Olist.

Sumber:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

File yang digunakan:
- olist_orders_dataset.csv
- olist_order_items_dataset.csv
- olist_products_dataset.csv

## 3. Instalasi

Buat virtual environment:

python -m venv venv

Aktifkan:

.\venv\Scripts\activate

Instal library:

pip install -r requirements.txt

## 4. Menjalankan ETL

Jalankan dari folder utama proyek:

python -m scripts.etl_pipeline

## 5. Pemeriksaan Data Quality

python -m scripts.quality_check

## 6. Data Analytics

Buka database:

analytics/ecommerce.duckdb

Jalankan perintah SQL pada:

analytics/analysis.sql

## 7. Hasil

Bronze:
Data mentah dalam format Parquet.

Silver:
Data yang sudah dibersihkan dan diintegrasikan.

Gold:
Hasil analisis penjualan dalam format Parquet.

DuckDB:
Database untuk pengolahan dan analisis data.

## 8. Data Quality

Pemeriksaan dilakukan terhadap:

1. Completeness
2. Accuracy
3. Consistency