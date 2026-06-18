CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- DIMENSIONES
-- ============================================================

CREATE TABLE dim_product (
    id INT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    cost_price DECIMAL(10,2),
    sale_price DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE dim_store (
    id INT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    region VARCHAR(100),
    city VARCHAR(100),
    type VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20),
    day INT NOT NULL,
    day_of_week INT,
    quarter INT,
    is_weekend BOOLEAN DEFAULT false,
    is_holiday BOOLEAN DEFAULT false
);

-- ============================================================
-- TABLA DE HECHOS
-- ============================================================

CREATE TABLE fact_sales (
    id BIGSERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES dim_product(id),
    store_id INT NOT NULL REFERENCES dim_store(id),
    date_id DATE NOT NULL REFERENCES dim_date(date_id),
    units_sold INT NOT NULL DEFAULT 0,
    revenue DECIMAL(12,2) NOT NULL DEFAULT 0,
    cost DECIMAL(12,2) NOT NULL DEFAULT 0,
    profit DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    customer_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_fact_sales_date ON fact_sales(date_id);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_id);
CREATE INDEX idx_fact_sales_store ON fact_sales(store_id);

-- ============================================================
-- KPIs
-- ============================================================

CREATE TABLE kpi_definitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    formula TEXT,
    unit VARCHAR(50) NOT NULL,
    frequency VARCHAR(20) NOT NULL DEFAULT 'daily',
    higher_is_better BOOLEAN DEFAULT true
);

CREATE TABLE kpi_results (
    id BIGSERIAL PRIMARY KEY,
    kpi_id INT NOT NULL REFERENCES kpi_definitions(id),
    date_id DATE NOT NULL REFERENCES dim_date(date_id),
    product_id INT REFERENCES dim_product(id),
    store_id INT REFERENCES dim_store(id),
    value DECIMAL(14,4) NOT NULL,
    previous_value DECIMAL(14,4),
    change_pct DECIMAL(8,4),
    calculated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_kpi_results_kpi_date ON kpi_results(kpi_id, date_id);

-- ============================================================
-- INSIGHTS Y REPORTES
-- ============================================================

CREATE TABLE insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    summary TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',
    related_kpi_ids INT[],
    date_id DATE REFERENCES dim_date(date_id),
    generated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    summary TEXT,
    content JSONB,
    html_content TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ
);

-- ============================================================
-- CONTROL ETL
-- ============================================================

CREATE TABLE etl_control (
    id SERIAL PRIMARY KEY,
    source_table VARCHAR(100) NOT NULL UNIQUE,
    last_max_id BIGINT DEFAULT 0,
    last_max_date DATE,
    last_run_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'pending'
);

-- ============================================================
-- SEED: KPI DEFINITIONS
-- ============================================================

INSERT INTO kpi_definitions (name, description, formula, unit, frequency, higher_is_better) VALUES
    ('total_revenue',   'Ingresos totales del período',           'SUM(revenue)',                          'COP',   'daily', true),
    ('total_profit',    'Ganancia bruta del período',             'SUM(profit)',                           'COP',   'daily', true),
    ('profit_margin',   'Margen de ganancia %',                   'SUM(profit)/SUM(revenue)*100',          '%',     'daily', true),
    ('units_sold',      'Unidades vendidas totales',              'SUM(units_sold)',                       'units', 'daily', true),
    ('avg_ticket',      'Ticket promedio por venta',              'SUM(revenue)/SUM(customer_count)',       'COP',   'daily', true),
    ('revenue_growth',  'Crecimiento de ingresos vs día anterior','((current - previous)/previous)*100',    '%',     'daily', true),
    ('profit_growth',   'Crecimiento de ganancia vs día anterior','((current - previous)/previous)*100',    '%',     'daily', true),
    ('discount_rate',   'Porcentaje de descuento aplicado',       'SUM(discount_amount)/SUM(revenue)*100',  '%',     'daily', false),
    ('margin_by_category','Margen por categoría de producto',     'AVG(profit/revenue)*100',               '%',     'daily', true),
    ('top_product',     'Producto más vendido del período',       'MAX(units_sold) by product',            'units', 'daily', true);

-- ============================================================
-- SEED: dim_date (10 años)
-- ============================================================

INSERT INTO dim_date (date_id, year, month, month_name, day, day_of_week, quarter, is_weekend)
SELECT
    d::DATE AS date_id,
    EXTRACT(YEAR FROM d)::INT AS year,
    EXTRACT(MONTH FROM d)::INT AS month,
    TO_CHAR(d, 'Month') AS month_name,
    EXTRACT(DAY FROM d)::INT AS day,
    EXTRACT(DOW FROM d)::INT AS day_of_week,
    EXTRACT(QUARTER FROM d)::INT AS quarter,
    EXTRACT(DOW FROM d) IN (0, 6) AS is_weekend
FROM generate_series(
    '2020-01-01'::DATE,
    '2030-12-31'::DATE,
    '1 day'::INTERVAL
) AS d;

-- ============================================================
-- DATOS DE PRUEBA (para desarrollo sin SQL Server)
-- ============================================================

INSERT INTO dim_product (id, name, category, subcategory, brand, cost_price, sale_price) VALUES
    (1, 'Laptop Pro X1',   'Electrónica', 'Laptops',    'TechBrand',  800.00, 1499.99),
    (2, 'Mouse Inalámbrico','Electrónica','Accesorios',  'TechBrand',  15.00,   49.99),
    (3, 'Teclado Mecánico','Electrónica', 'Accesorios',  'KeyCo',      35.00,   89.99),
    (4, 'Monitor 27" 4K',  'Electrónica', 'Monitores',   'ViewPro',    250.00,  499.99),
    (5, 'Audífonos BT',    'Electrónica', 'Audio',       'SoundMax',   40.00,   99.99),
    (6, 'Camiseta Algodón','Ropa',       'Camisetas',    'CottonCo',    8.00,   29.99),
    (7, 'Jeans Clásicos',  'Ropa',       'Pantalones',   'DenimCo',    20.00,   59.99),
    (8, 'Chaqueta Invierno','Ropa',      'Chaquetas',    'WarmWear',   45.00,  129.99),
    (9, 'Zapatos Deportivos','Calzado',  'Deportivo',    'RunFast',    35.00,   89.99),
    (10,'Sandalias Verano','Calzado',    'Casual',       'ComfortStep',12.00,   39.99);

INSERT INTO dim_store (id, name, region, city, type) VALUES
    (1, 'Centro Bogotá',    'Andina',     'Bogotá',     'física'),
    (2, 'Portal Norte',     'Andina',     'Bogotá',     'física'),
    (3, 'Plaza Medellín',  'Andina',     'Medellín',   'física'),
    (4, 'Calle 80',         'Caribe',     'Barranquilla','física'),
    (5, 'Mall del Pacífico','Pacífica',   'Cali',       'física'),
    (6, 'Tienda Online',    'Nacional',   'Virtual',    'online'),
    (7, 'Centro Bucaramanga','Oriental',  'Bucaramanga','física'),
    (8, 'Plaza 25',         'Pacífica',   'Cali',       'física');

INSERT INTO fact_sales (product_id, store_id, date_id, units_sold, revenue, cost, profit, discount_amount, customer_count)
SELECT
    (random() * 9 + 1)::INT AS product_id,
    (random() * 7 + 1)::INT AS store_id,
    d::DATE AS date_id,
    (random() * 5 + 1)::INT AS units_sold,
    (random() * 500 + 50)::DECIMAL(10,2) AS revenue,
    (random() * 300 + 20)::DECIMAL(10,2) AS cost,
    (random() * 200 + 10)::DECIMAL(10,2) AS profit,
    (random() * 20)::DECIMAL(10,2) AS discount_amount,
    (random() * 3 + 1)::INT AS customer_count
FROM generate_series(
    CURRENT_DATE - INTERVAL '90 days',
    CURRENT_DATE - INTERVAL '1 day',
    '1 day'::INTERVAL
) AS d
CROSS JOIN generate_series(1, 20) AS n;

