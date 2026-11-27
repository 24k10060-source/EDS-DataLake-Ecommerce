-- ==========================================
-- 1. MENGHITUNG JUMLAH TRANSAKSI
-- ==========================================

SELECT
    COUNT(DISTINCT order_id) AS total_transaksi
FROM ecommerce_silver;

-- ==========================================
-- 2. MENGHITUNG TOTAL PENJUALAN
-- ==========================================

SELECT
    ROUND(SUM(price), 2) AS total_penjualan
FROM ecommerce_silver;

-- ==========================================
-- 3. MENGETAHUI PRODUK PALING BANYAK TERJUAL
-- ==========================================

SELECT
    product_id,
    product_category_name,
    COUNT(*) AS jumlah_terjual
FROM ecommerce_silver
GROUP BY
    product_id,
    product_category_name
ORDER BY jumlah_terjual DESC
LIMIT 10;

-- ==========================================
-- 4. MENGANALISIS PENJUALAN BERDASARKAN PERIODE
-- ==========================================

SELECT
    order_month,
    COUNT(DISTINCT order_id) AS total_transaksi,
    ROUND(SUM(price), 2) AS total_penjualan
FROM ecommerce_silver
WHERE order_month IS NOT NULL
  AND order_month != 'NaT'
GROUP BY order_month
ORDER BY order_month;

-- ==========================================
-- 5. KATEGORI PRODUK DENGAN PENJUALAN TERTINGGI
-- ==========================================

SELECT
    product_category_name,
    COUNT(*) AS jumlah_item,
    ROUND(SUM(price), 2) AS total_penjualan
FROM ecommerce_silver
GROUP BY product_category_name
ORDER BY total_penjualan DESC
LIMIT 10;

-- ==========================================
-- 6. RINGKASAN HASIL ANALISIS
-- ==========================================

SELECT *
FROM gold_sales_summary;