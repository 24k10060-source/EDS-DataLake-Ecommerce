import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SILVER_FILE = (
    BASE_DIR
    / "data_lake"
    / "silver"
    / "ecommerce_silver.parquet"
)

def check_quality():

    print("\n====================================")
    print("       DATA QUALITY REPORT")
    print("====================================")

    if not SILVER_FILE.exists():
        print("Data Silver belum tersedia.")
        print("Jalankan ETL Pipeline terlebih dahulu.")
        return

    df = pd.read_parquet(SILVER_FILE)

    # --------------------------------
    # 1. COMPLETENESS
    # --------------------------------

    print("\n1. COMPLETENESS")

    total_data = len(df)

    missing = df.isnull().sum()

    print("Jumlah data:", total_data)
    print("\nNilai kosong setiap kolom:")

    print(missing)

    # --------------------------------
    # 2. ACCURACY
    # --------------------------------

    print("\n2. ACCURACY")

    negative_price = (df["price"] < 0).sum()

    invalid_date = (
        df["order_purchase_timestamp"].isna().sum()
    )

    print("Harga negatif:", negative_price)
    print("Tanggal tidak valid:", invalid_date)

    # --------------------------------
    # 3. CONSISTENCY
    # --------------------------------

    print("\n3. CONSISTENCY")

    invalid_order = (
        df["order_id"].astype(str).str.strip() == ""
    ).sum()

    invalid_product = (
        df["product_id"].astype(str).str.strip() == ""
    ).sum()

    print("Order ID kosong:", invalid_order)
    print("Product ID kosong:", invalid_product)

    # --------------------------------
    # RINGKASAN
    # --------------------------------

    print("\n====================================")
    print("       RINGKASAN KUALITAS")
    print("====================================")

    print("Completeness: Pemeriksaan selesai")
    print("Accuracy: Pemeriksaan selesai")
    print("Consistency: Pemeriksaan selesai")

    print("\nPemeriksaan kualitas data selesai.")

if __name__ == "__main__":
    check_quality()