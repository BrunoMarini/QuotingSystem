import sqlite3
from sqlite3 import Connection

# Responsible to generate the dictionary from Query results
def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class ServiceDatabase:
    def __init__(self):
        self.connection = sqlite3.connect('./data/quotation_system.db', check_same_thread=False)
        self.connection.row_factory = _dict_factory
        self.cursor = self.connection.cursor()
        self.create_tables_if_not_exists()

    def create_tables_if_not_exists(self):
        # Create Customer table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Customer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT)''')

        # Create Quotation table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Quotation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                status TEXT CHECK(status IN ('open', 'closed', 'canceled')) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES Customer(id))''')

        # Create QuotationItem table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS QuotationItem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quotation_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (quotation_id) REFERENCES Quotation(id),
                FOREIGN KEY (service_id) REFERENCES Service(id))''')

        # Create Service table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Service (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                price REAL NOT NULL)''')

        self.connection.commit()

    # Create new Customer
    def create_customer(self, name, email=None, phone=None, address=None):
        self.cursor.execute('''
            INSERT INTO Customer (name, email, phone, address)
            VALUES (?, ?, ?, ?)''', (name, email, phone, address))
        self.connection.commit()

    # Create new Quotation
    def create_quotation(self, customer_id):
        self.cursor.execute('''
            INSERT INTO Quotation (customer_id, status)
            VALUES (?, ?)''', (customer_id, 'open'))
        self.connection.commit()

    # Create new Service
    def create_service(self, name, price, description=None):
        self.cursor.execute('''
            INSERT INTO Service (name, description, price)
            VALUES (?, ?, ?)''', (name, description, price))
        self.connection.commit()

    # Add Item to Quotation
    def add_item(self, quotation_id: int, service_id: int, quantity: int) -> bool:
        try:
            service_price = self.get_price_for_service_id(service_id)
            if service_price <= 0:
                return -1

            item = self.get_item_for_quotation_and_service_id(quotation_id, service_id)
            if item:
                id = item['id']
                quantity += item['quantity']
                total_price = service_price * quantity
                self.cursor.execute(f'UPDATE QuotationItem SET quantity = {quantity}, total_price = {total_price} WHERE id = {id}')
                self.connection.commit()
                return 1

            total_price = quantity * service_price
            self.cursor.execute('''
                INSERT INTO QuotationItem (quotation_id, service_id, quantity, total_price)
                VALUES (?, ?, ?, ?)''', (quotation_id, service_id, quantity, total_price))
            return total_price
        except Exception as e:
            print("Failed to add_item()", e)
            return -1

    #
    def get_price_for_service_id(self, service_id):
        try:
            self.cursor.execute(f'SELECT price FROM service WHERE id = {service_id}')
            result = self.cursor.fetchone()
            if result:
                return result['price']
            return -1
        except Exception as e:
            print(f"Failed to get_price_for_service_id({service_id})", e)
            return -1

    #
    def get_item_for_quotation_and_service_id(self, quotation_id, service_id):
        try:
            self.cursor.execute('''
                SELECT * FROM QuotationItem WHERE
                quotation_id = ? AND
                service_id = ?''', (quotation_id, service_id))
            result = self.cursor.fetchone()
            if result:
                return result
            return None
        except Exception as e:
            print(f"Failed to get_quotation_item_for_quotation_and_service_id({quotation_id})", e)
            return None

    # Move Quotation to status 'closed'
    def close_quotation(self, quotation_id):
        self.cursor.execute('''
            UPDATE Quotation
            SET status = 'closed', closed_at = CURRENT_TIMESTAMP
            WHERE id = ?''', (quotation_id,))
        self.connection.commit()

    # Retrieve all open Quotations
    def get_open_quotations(self):
        self.cursor.execute('SELECT * FROM Quotation WHERE status = "open"')
        return self.cursor.fetchall()

    # Returns
    # id - Quotation ID
    # name - Customer Name
    # total_price - Quotation Total Price
    # created_at - Date when quotation was created
    def get_open_quotations_with_customer_and_price(self):
        self.cursor.execute('''
            SELECT q.id as id, c.name AS name, COALESCE(SUM(qi.total_price), 0) AS total_price, strftime('%H:%M %d/%m/%Y', q.created_at) AS created_at
            FROM
                Quotation q 
            JOIN
                Customer c ON q.customer_id = c.id
            LEFT JOIN
                QuotationItem qi ON q.id = qi.quotation_id
            WHERE
                q.status = 'open'
            GROUP BY
                c.name, q.created_at''')
        return self.cursor.fetchall()

    #
    def get_all_items_for_quotation(self, quotation_id):
        self.cursor.execute(f'SELECT * FROM QuotationItem WHERE quotation_id = {quotation_id}')
        return self.cursor.fetchall()

    #
    def get_all_services(self):
        self.cursor.execute('SELECT * from Service')
        return self.cursor.fetchall()

    #
    def get_service_for_id(self, service_id):
        self.cursor.execute(f'SELECT * from Service WHERE id = {service_id}')
        return self.cursor.fetchone()

    #
    def delete_quotation_item(self, item_id, quotation_id):
        try:
            self.cursor.execute(f'DELETE FROM QuotationItem WHERE id = {item_id}')
            self.connection.commit()
            return self.get_quotation_total_price(quotation_id)
        except Exception as e:
            print("Failed to delete_quotation_item", e)

    def get_quotation_total_price(self, quotation_id):
        total_price = 0
        items = self.get_all_items_for_quotation(quotation_id)
        for item in items:
            quantity = item['quantity']
            service_id = item['service_id']
            total_price += quantity * self.get_price_for_service_id(service_id)
        return total_price




    # TODO: Add sample data, DELETE
    def add_sample_data(self):
        self.cursor.execute('DELETE FROM Customer')
        self.cursor.execute('DELETE FROM Quotation')
        self.cursor.execute('DELETE FROM QuotationItem')
        self.cursor.execute('DELETE FROM Service')
        self.connection.commit()

        # Add sample customers
        self.create_customer('Alice Smith', 'alice@example.com', '555-1234', '123 Elm Street')
        self.create_customer('Bob Johnson', 'bob@example.com', '555-5678', '456 Oak Avenue')
        self.create_customer('Carol Williams', 'carol@example.com', '555-8765', '789 Pine Road')
        self.create_customer('Caro4l Williams', 'carol@example.com', '555-8765', '789 Pine Road')
        self.create_customer('Car3ol Williams', 'carol@example.com', '555-8765', '789 Pine Road')
        self.create_customer('Ca2rol Williams', 'carol@example.com', '555-8765', '789 Pine Road')
        self.create_customer('C1arol Williams', 'carol@example.com', '555-8765', '789 Pine Road')

        # Retrieve customer IDs
        self.cursor.execute('SELECT id FROM Customer')
        customer_ids = [row['id'] for row in self.cursor.fetchall()]

        # Add sample services
        self.create_service('Oil Change', 29.99, 'Change engine oil')
        self.create_service('Tire Rotation', 19.99, 'Rotate tires for even wear')
        self.create_service('Brake Inspection', 49.99, 'Inspect and test brake system')

        # Retrieve service IDs
        self.cursor.execute('SELECT id FROM Service')
        service_ids = [row['id'] for row in self.cursor.fetchall()]

        # Add sample quotations
        quotation_ids = []
        for customer_id in customer_ids:
            self.create_quotation(customer_id)
            self.cursor.execute('SELECT id FROM Quotation WHERE customer_id = ?', (customer_id,))
            quotation_ids.append(self.cursor.fetchone()['id'])

        # Add sample items to quotations
        if len(quotation_ids) > 0 and len(service_ids) > 0:
            self.add_item(quotation_ids[0], service_ids[0], 1)
            self.add_item(quotation_ids[0], service_ids[1], 2)
            if len(quotation_ids) > 1:
                self.add_item(quotation_ids[1], service_ids[2], 1)
            if len(quotation_ids) > 2:
                self.add_item(quotation_ids[2], service_ids[0], 2)
                self.add_item(quotation_ids[2], service_ids[1], 1)

        self.connection.commit()




    def __del__(self):
        self.connection.close()