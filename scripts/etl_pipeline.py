import pandas as pd
import duckdb
from pathlib import Path

# ==========================================
# 1. KONFIGURASI FOLDER
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "dataset" / "raw"
BRONZE_DIR = BASE_DIR / "data_lake" / "bronze"
SILVER_DIR = BASE_DIR / "data_lake" / "silver"
GOLD_DIR = BASE_DIR / "data_lake" / "gold"
ANALYTICS_DIR = BASE_DIR / "analytics"

DB_PATH = ANALYTICS_DIR / "ecommerce.duckdb"

# Membuat folder jika belum tersedia
for folder in [
    BRONZE_DIR,
    SILVER_DIR,
    GOLD_DIR,
    ANALYTICS_DIR
]:
    folder.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. EXTRACT
# Mengambil data CSV dari Olist
# ==========================================

def extract_data():

    print("\n========== PROSES EXTRACT ==========")

    files = [
        "olist_orders_dataset.csv",
        "olist_order_items_dataset.csv",
        "olist_products_dataset.csv"
    ]

    for filename in files:

        csv_path = RAW_DIR / filename

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Dataset tidak ditemukan: {csv_path}"
            )

        df = pd.read_csv(csv_path)

        parquet_name = filename.replace(".csv", ".parquet")
        output_path = BRONZE_DIR / parquet_name

        df.to_parquet(
            output_path,
            index=False
        )

        print(f"Berhasil mengambil: {filename}")
        print(f"Jumlah baris: {len(df):,}")
        print(f"Disimpan ke: {output_path}")

# ==========================================
# 3. TRANSFORM
# Membersihkan dan mengintegrasikan data
# ==========================================

def transform_data():

    print("\n========== PROSES TRANSFORM ==========")

    orders = pd.read_parquet(
        BRONZE_DIR / "olist_orders_dataset.parquet"
    )

    items = pd.read_parquet(
        BRONZE_DIR / "olist_order_items_dataset.parquet"
    )

    products = pd.read_parquet(
        BRONZE_DIR / "olist_products_dataset.parquet"
    )

    # Menghapus data duplikat
    orders = orders.drop_duplicates(
        subset=["order_id"]
    )

    items = items.drop_duplicates(
        subset=["order_id", "order_item_id"]
    )

    products = products.drop_duplicates(
        subset=["product_id"]
    )

    # Menghapus data penting yang kosong
    orders = orders.dropna(
        subset=["order_id", "customer_id"]
    )

    items = items.dropna(
        subset=["order_id", "product_id", "price"]
    )

    products = products.dropna(
        subset=["product_id"]
    )

    # Mengubah format tanggal
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce"
    )

    # Mengubah harga menjadi numerik
    items["price"] = pd.to_numeric(
        items["price"],
        errors="coerce"
    )

    # Menghapus harga yang tidak valid
    items = items.dropna(
        subset=["price"]
    )

    items = items[items["price"] >= 0]

    # Mengintegrasikan orders dan items
    merged_data = pd.merge(
        orders,
        items,
        on="order_id",
        how="inner"
    )

    # Mengintegrasikan products
    merged_data = pd.merge(
        merged_data,
        products,
        on="product_id",
        how="left"
    )

    # Menangani kategori produk kosong
    merged_data["product_category_name"] = (
        merged_data["product_category_name"]
        .fillna("Unknown")
    )

    # Menambahkan kolom periode transaksi
    merged_data["order_month"] = (
        merged_data["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    # Menyimpan data Silver
    silver_path = SILVER_DIR / "ecommerce_silver.parquet"

    merged_data.to_parquet(
        silver_path,
        index=False
    )

    print("Transform berhasil!")
    print(f"Jumlah data Silver: {len(merged_data):,}")
    print(f"Data disimpan: {silver_path}")

# ==========================================
# 4. LOAD
# Memuat data ke DuckDB
# dan menghasilkan Gold
# ==========================================

def load_data():

    print("\n========== PROSES LOAD ==========")

    con = duckdb.connect(str(DB_PATH))

    silver_path = (
        str(SILVER_DIR / "ecommerce_silver.parquet")
        .replace("\\", "/")
    )

    # Membuat tabel Silver di DuckDB
    con.execute(f"""
        CREATE OR REPLACE TABLE ecommerce_silver AS
        SELECT *
        FROM read_parquet('{silver_path}')
    """)

    # --------------------------------------
    # GOLD 1: RINGKASAN PENJUALAN
    # --------------------------------------

    con.execute("""
        CREATE OR REPLACE TABLE gold_sales_summary AS
        SELECT
            COUNT(DISTINCT order_id) AS total_transaksi,
            COUNT(*) AS total_item_terjual,
            ROUND(SUM(price), 2) AS total_penjualan,
            ROUND(AVG(price), 2) AS rata_rata_harga
        FROM ecommerce_silver
    """)

    # --------------------------------------
    # GOLD 2: PENJUALAN PER BULAN
    # --------------------------------------

    con.execute("""
        CREATE OR REPLACE TABLE gold_monthly_sales AS
        SELECT
            order_month,
            COUNT(DISTINCT order_id) AS total_transaksi,
            COUNT(*) AS jumlah_item,
            ROUND(SUM(price), 2) AS total_penjualan
        FROM ecommerce_silver
        WHERE order_month IS NOT NULL
          AND order_month != 'NaT'
        GROUP BY order_month
        ORDER BY order_month
    """)

    # --------------------------------------
    # GOLD 3: PRODUK TERLARIS
    # --------------------------------------

    con.execute("""
        CREATE OR REPLACE TABLE gold_top_products AS
        SELECT
            product_id,
            product_category_name,
            COUNT(*) AS jumlah_terjual,
            ROUND(SUM(price), 2) AS total_penjualan
        FROM ecommerce_silver
        GROUP BY
            product_id,
            product_category_name
        ORDER BY jumlah_terjual DESC
        LIMIT 10
    """)

    # --------------------------------------
    # GOLD 4: PENJUALAN PER KATEGORI
    # --------------------------------------

    con.execute("""
        CREATE OR REPLACE TABLE gold_category_sales AS
        SELECT
            product_category_name,
            COUNT(*) AS jumlah_item,
            ROUND(SUM(price), 2) AS total_penjualan
        FROM ecommerce_silver
        GROUP BY product_category_name
        ORDER BY total_penjualan DESC
    """)

    # --------------------------------------
    # MENYIMPAN HASIL GOLD KE PARQUET
    # --------------------------------------

    tables = [
        "gold_sales_summary",
        "gold_monthly_sales",
        "gold_top_products",
        "gold_category_sales"
    ]

    for table in tables:

        output_path = (
            str(GOLD_DIR / f"{table}.parquet")
            .replace("\\", "/")
        )

        con.execute(f"""
            COPY {table}
            TO '{output_path}'
            (FORMAT PARQUET)
        """)

        print(f"Berhasil membuat {table}.parquet")

    con.close()

    print("Load berhasil!")
    print(f"Database DuckDB: {DB_PATH}")

# ==========================================
# 5. MENJALANKAN SELURUH ETL
# ==========================================

if __name__ == "__main__":

    print("======================================")
    print(" EDS DATA LAKE E-COMMERCE")
    print(" PYTHON - DUCKDB - APACHE PARQUET")
    print("======================================")

    extract_data()

    transform_data()

    load_data()

    print("\n======================================")
    print("SELURUH PROSES ETL BERHASIL!")
    print("======================================")