-- Drop tables in the correct order to avoid foreign key issues
DROP TABLE IF EXISTS QuotationItems;
DROP TABLE IF EXISTS Quotations;
DROP TABLE IF EXISTS Items;
DROP TABLE IF EXISTS Clients;
DROP TABLE IF EXISTS AvailableServices;

-- Create tables
CREATE TABLE IF NOT EXISTS Clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT
);

CREATE TABLE IF NOT EXISTS Quotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('open', 'closed')) NOT NULL,
    items TEXT,  -- This field stores JSON or serialized item data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    total_amount REAL DEFAULT 0.00,
    FOREIGN KEY (client_id) REFERENCES Clients(id)
);

CREATE TABLE IF NOT EXISTS Items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL--,
    --total_price REAL GENERATED ALWAYS AS (quantity * unit_price) STORED
);

CREATE TABLE IF NOT EXISTS AvailableServices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    unit_price REAL NOT NULL
);

-- Insert Customers
INSERT INTO Clients (name) VALUES ('Bruno');
INSERT INTO Clients (name) VALUES ('Pedro');
INSERT INTO Clients (name) VALUES ('Mirko');

-- Insert Available Services
INSERT INTO AvailableServices (name, description, unit_price) VALUES ('Revisão Simples', 'RS', 50);
INSERT INTO AvailableServices (name, description, unit_price) VALUES ('Revisão Completa', 'RC', 100);
INSERT INTO AvailableServices (name, description, unit_price) VALUES ('Revisão Suspensão', 'RSus', 150);

-- Insert a quotation
INSERT INTO Quotations (client_id, status) VALUES (1, 'open');
INSERT INTO Quotations (client_id, status) VALUES (2, 'open');

INSERT into Items (service_id, quantity) VALUES (3, 1);
INSERT into Items (service_id, quantity) VALUES (3, 1);

UPDATE TABLE Quotations set WHERE id = (SELECT id from Quotations where client_id = 1 AND status = 'open')


UPDATE table_name
SET column1 = value1, column2 = value2...., columnN = valueN
WHERE [condition];