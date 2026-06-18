-- ============================================================
-- ESQUEMA SQL SERVER (fuente de datos retail)
-- ============================================================

CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    cost_price DECIMAL(10,2),
    sale_price DECIMAL(10,2)
);

CREATE TABLE stores (
    id INT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    region VARCHAR(100),
    city VARCHAR(100),
    type VARCHAR(50)
);

CREATE TABLE sales (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id),
    store_id INT NOT NULL REFERENCES stores(id),
    customer_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    sale_date DATE NOT NULL,
    sale_hour TIME DEFAULT NULL
);

CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_product ON sales(product_id);
CREATE INDEX idx_sales_store ON sales(store_id);

-- ============================================================
-- DATOS DE PRUEBA
-- ============================================================

INSERT INTO products (id, name, category, subcategory, brand, cost_price, sale_price) VALUES
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

INSERT INTO stores (id, name, region, city, type) VALUES
    (1, 'Centro Bogotá',    'Andina',     'Bogotá',     'física'),
    (2, 'Portal Norte',     'Andina',     'Bogotá',     'física'),
    (3, 'Plaza Medellín',   'Andina',     'Medellín',   'física'),
    (4, 'Calle 80',         'Caribe',     'Barranquilla','física'),
    (5, 'Mall del Pacífico','Pacífica',   'Cali',       'física'),
    (6, 'Tienda Online',    'Nacional',   'Virtual',    'online'),
    (7, 'Centro Bucaramanga','Oriental',  'Bucaramanga','física'),
    (8, 'Plaza 25',         'Pacífica',   'Cali',       'física');

-- 90 días de ventas simuladas
DECLARE @start DATE = DATEADD(DAY, -90, CAST(GETDATE() AS DATE));
DECLARE @end DATE = DATEADD(DAY, -1, CAST(GETDATE() AS DATE));
DECLARE @d DATE = @start;

WHILE @d <= @end
BEGIN
    DECLARE @n INT = 0;
    WHILE @n < 20
    BEGIN
        DECLARE @pid INT = CAST((RAND() * 9 + 1) AS INT);
        DECLARE @sid INT = CAST((RAND() * 7 + 1) AS INT);
        DECLARE @qty INT = CAST((RAND() * 5 + 1) AS INT);
        DECLARE @price DECIMAL(10,2) = ROUND(RAND() * 500 + 50, 2);
        DECLARE @disc DECIMAL(10,2) = ROUND(RAND() * 20, 2);
        DECLARE @cust INT = CAST((RAND() * 3 + 1) AS INT);

        INSERT INTO sales (product_id, store_id, customer_id, quantity, unit_price, discount, total, sale_date)
        VALUES (@pid, @sid, @cust, @qty, @price, @disc, @price * @qty - @disc, @d);

        SET @n = @n + 1;
    END;
    SET @d = DATEADD(DAY, 1, @d);
END;
