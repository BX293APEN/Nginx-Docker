-- ============================================================
-- テーブル定義
-- ============================================================

-- 商品テーブル
CREATE TABLE Commodity (
    c_code CHAR(4) PRIMARY KEY,
    c_kind VARCHAR(20) NOT NULL,
    c_name VARCHAR(50) NOT NULL,
    price  INTEGER NOT NULL
);

-- 卸業者テーブル
CREATE TABLE Dealer (
    d_code  CHAR(4) PRIMARY KEY,
    d_name  VARCHAR(50) NOT NULL,
    address VARCHAR(100) NOT NULL
);

-- 仕入テーブル
CREATE TABLE Supply (
    c_code      CHAR(4) NOT NULL,
    d_code      CHAR(4) NOT NULL,
    quantity    INTEGER NOT NULL,
    supply_date DATE NOT NULL,
    FOREIGN KEY (c_code) REFERENCES Commodity(c_code),
    FOREIGN KEY (d_code) REFERENCES Dealer(d_code)
);

-- 受注テーブル
CREATE TABLE Orders (
    c_code     CHAR(4) NOT NULL,
    d_code     CHAR(4) NOT NULL,
    quantity   INTEGER NOT NULL,
    order_date DATE NOT NULL,
    FOREIGN KEY (c_code) REFERENCES Commodity(c_code),
    FOREIGN KEY (d_code) REFERENCES Dealer(d_code)
);

-- ============================================================
-- データ登録
-- ============================================================

-- Commodity
INSERT INTO Commodity (c_code, c_kind, c_name, price) VALUES
('1233', '食料品',       '食パン',       200),
('1234', '日用品',       'セッケン',     180),
('1235', '日用品',       '歯ブラシ',     150),
('1357', '冷凍食品',     '冷凍コロッケ', 300),
('2468', '野菜',         'キャベツ',     99),
('3456', 'オフィス用品', 'イス',         9000);

-- Dealer
INSERT INTO Dealer (d_code, d_name, address) VALUES
('1111', '井上卸',   '川崎市川崎区'),
('6767', '鈴木販売', '名古屋市北区'),
('7777', '伊藤商店', '神戸市灘区'),
('9641', '山田産業', '大阪市中央区'),
('9876', '田中商事', '東京都港区');

-- Supply
INSERT INTO Supply (c_code, d_code, quantity, supply_date) VALUES
('1234', '9641', 10, '1997-10-12'),
('1357', '9876', 50, '1997-08-22'),
('2468', '9876', 30, '1997-09-01');

-- Orders
INSERT INTO Orders (c_code, d_code, quantity, order_date) VALUES
('1233', '9876', 10, '1997-09-01'),
('1234', '9876', 20, '1997-08-10'),
('1235', '9641', 40, '1997-10-25'),
('2468', '9641', 200, '1997-09-01'),
('2468', '9641', 30, '1997-11-02');
