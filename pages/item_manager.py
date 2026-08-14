from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTabWidget, QFormLayout, 
                             QMessageBox, QScrollArea)
from datetime import date
import mysql.connector
import db
import session

class ItemManagerPage(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # this tab manages items 
        self.manage_tab = QWidget()
        self.setup_manage_tab()
        self.tabs.addTab(self.manage_tab, "Manage My Items")

        # second tab handles the advanced queries 1 2 and 4
        self.queries_tab = QWidget()
        self.setup_queries_tab()
        self.tabs.addTab(self.queries_tab, "Advanced Queries")

        self.layout.addWidget(self.tabs)
        
        self.back_button = QPushButton("Back to Welcome")
        self.layout.addWidget(self.back_button)

        self.setLayout(self.layout)

    
    # part 1 and 2 item managment   
    def setup_manage_tab(self):
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        form = QFormLayout()

        # Add New Item 
        self.add_title = QLineEdit()
        self.add_desc = QLineEdit()
        self.add_price = QLineEdit()
        self.add_cats = QLineEdit()
        self.add_cats.setPlaceholderText("Comma separated (e.g., Electronics, Gadgets)")
        self.btn_add_item = QPushButton("Add Item")
        self.btn_add_item.clicked.connect(self.add_item)

        form.addRow(QLabel("<b>Add New Item</b>"))
        form.addRow("Title:", self.add_title)
        form.addRow("Description:", self.add_desc)
        form.addRow("Price ($):", self.add_price)
        form.addRow("Categories:", self.add_cats)
        form.addRow(self.btn_add_item)
        form.addRow(QLabel("<hr>"))

        # Update Item Price 
        self.upd_item_id = QLineEdit()
        self.upd_price = QLineEdit()
        self.btn_upd_price = QPushButton("Update Price")
        self.btn_upd_price.clicked.connect(self.update_price)

        form.addRow(QLabel("<b>Update Item Price</b>"))
        form.addRow("Item ID:", self.upd_item_id)
        form.addRow("New Price ($):", self.upd_price)
        form.addRow(self.btn_upd_price)
        form.addRow(QLabel("<hr>"))

        # This button for deleting items
        self.del_item_id = QLineEdit()
        self.btn_delete = QPushButton("Delete Item")
        self.btn_delete.clicked.connect(self.delete_item)

        form.addRow(QLabel("<b>Delete Item</b>"))
        form.addRow("Item ID:", self.del_item_id)
        form.addRow(self.btn_delete)
        form.addRow(QLabel("<hr>"))

        # --- Category Management ---
        self.cat_item_id = QLineEdit()
        self.cat_name = QLineEdit()
        
        cat_buttons = QHBoxLayout()
        self.btn_add_cat = QPushButton("Add Category")
        self.btn_add_cat.clicked.connect(lambda: self.manage_category("add"))
        self.btn_rm_cat = QPushButton("Remove Category")
        self.btn_rm_cat.clicked.connect(lambda: self.manage_category("remove"))
        cat_buttons.addWidget(self.btn_add_cat)
        cat_buttons.addWidget(self.btn_rm_cat)

        form.addRow(QLabel("<b>Assign/Remove Category</b>"))
        form.addRow("Item ID:", self.cat_item_id)
        form.addRow("Category:", self.cat_name)
        form.addRow(cat_buttons)

        container.setLayout(form)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        self.manage_tab.setLayout(layout)

    def add_item(self):
        if not session.current_user:
            QMessageBox.warning(self, "Error", "You must be logged in.")
            return

        title = self.add_title.text().strip()
        desc = self.add_desc.text().strip()
        price = self.add_price.text().strip()
        categories = [c.strip() for c in self.add_cats.text().split(",") if c.strip()]

        if not title or not price or not categories:
            QMessageBox.warning(self, "Error", "Title, price, and at least one category are required.")
            return

        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO item (title, description, price, datePosted, seller) VALUES (%s, %s, %s, %s, %s)",
                (title, desc, float(price), date.today(), session.current_user)
            )
            new_item_id = cursor.lastrowid

            for cat in categories:
                cursor.execute(
                    "INSERT INTO item_category (itemID, category) VALUES (%s, %s)",
                    (new_item_id, cat)
                )

            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Success", f"Item #{new_item_id} added successfully.")
            
            self.add_title.clear()
            self.add_desc.clear()
            self.add_price.clear()
            self.add_cats.clear()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", str(err.msg))
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Price must be a valid number.")

    def update_price(self):
        item_id = self.upd_item_id.text().strip()
        price = self.upd_price.text().strip()

        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE item SET price = %s WHERE itemID = %s AND seller = %s", 
                           (float(price), int(item_id), session.current_user))
            
            if cursor.rowcount == 0:
                QMessageBox.warning(self, "Error", "Item not found or you do not own it.")
            else:
                conn.commit()
                QMessageBox.information(self, "Success", "Price updated.")
            
            cursor.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_item(self):
        item_id = self.del_item_id.text().strip()
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM item WHERE itemID = %s AND seller = %s", 
                           (int(item_id), session.current_user))
            
            if cursor.rowcount == 0:
                QMessageBox.warning(self, "Error", "Item not found or you do not own it.")
            else:
                conn.commit()
                QMessageBox.information(self, "Success", "Item deleted.")
            
            cursor.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def manage_category(self, action):
        item_id = self.cat_item_id.text().strip()
        cat_name = self.cat_name.text().strip()

        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT itemID FROM item WHERE itemID = %s AND seller = %s", 
                           (int(item_id), session.current_user))
            if not cursor.fetchone():
                QMessageBox.warning(self, "Error", "Item not found or you do not own it.")
                return

            if action == "add":
                cursor.execute("INSERT IGNORE INTO item_category (itemID, category) VALUES (%s, %s)", 
                               (int(item_id), cat_name))
                msg = "Category added."
            elif action == "remove":
                cursor.execute("DELETE FROM item_category WHERE itemID = %s AND category = %s", 
                               (int(item_id), cat_name))
                msg = "Category removed."

            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Success", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    # part 4 SQL queries (1, 2, 4)
   
    def setup_queries_tab(self):
        layout = QVBoxLayout()

        self.q_results = QLabel("Results will appear here.")
        self.q_results.setWordWrap(True)
        self.q_results.setStyleSheet("background-color: white; border: 1px solid gray; padding: 10px;")

        # Query 1
        btn_q1 = QPushButton("Q1: Most Expensive Items by Category")
        btn_q1.clicked.connect(self.run_query_1)
        layout.addWidget(btn_q1)

        # Query 2
        q2_layout = QHBoxLayout()
        self.q2_cat_x = QLineEdit()
        self.q2_cat_x.setPlaceholderText("Category X")
        self.q2_cat_y = QLineEdit()
        self.q2_cat_y.setPlaceholderText("Category Y")
        btn_q2 = QPushButton("Q2: Find Users (Same Day, Diff Cats)")
        btn_q2.clicked.connect(self.run_query_2)
        q2_layout.addWidget(self.q2_cat_x)
        q2_layout.addWidget(self.q2_cat_y)
        q2_layout.addWidget(btn_q2)
        layout.addLayout(q2_layout)

        # Query 4
        q4_layout = QHBoxLayout()
        self.q4_date = QLineEdit()
        self.q4_date.setPlaceholderText("YYYY-MM-DD")
        btn_q4 = QPushButton("Q4: Top Posters by Date")
        btn_q4.clicked.connect(self.run_query_4)
        q4_layout.addWidget(self.q4_date)
        q4_layout.addWidget(btn_q4)
        layout.addLayout(q4_layout)

        layout.addWidget(QLabel("<b>Query Results:</b>"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.q_results)
        layout.addWidget(scroll)

        self.queries_tab.setLayout(layout)

    def run_query_1(self):
        sql = """
        SELECT c.category, i.title, i.price 
        FROM item_category c
        JOIN item i ON c.itemID = i.itemID
        WHERE i.price = (
            SELECT MAX(i2.price) 
            FROM item_category c2 
            JOIN item i2 ON c2.itemID = i2.itemID 
            WHERE c2.category = c.category
        )
        ORDER BY c.category;
        """
        self.execute_and_display(sql, (), "Category | Title | Price")

    def run_query_2(self):
        cat_x = self.q2_cat_x.text().strip()
        cat_y = self.q2_cat_y.text().strip()
        if not cat_x or not cat_y:
            QMessageBox.warning(self, "Error", "Provide both categories.")
            return

        sql = """
        SELECT DISTINCT i1.seller
        FROM item i1
        JOIN item_category c1 ON i1.itemID = c1.itemID
        JOIN item i2 ON i1.seller = i2.seller AND i1.datePosted = i2.datePosted
        JOIN item_category c2 ON i2.itemID = c2.itemID
        WHERE i1.itemID != i2.itemID 
          AND c1.category = %s 
          AND c2.category = %s;
        """
        self.execute_and_display(sql, (cat_x, cat_y), "Users")

    def run_query_4(self):
        date_str = self.q4_date.text().strip()
        if not date_str:
            QMessageBox.warning(self, "Error", "Provide a date (YYYY-MM-DD).")
            return

        sql = """
        SELECT seller, COUNT(*) as item_count 
        FROM item 
        WHERE datePosted = %s 
        GROUP BY seller 
        HAVING item_count = (
            SELECT MAX(c) FROM (
                SELECT COUNT(*) as c FROM item WHERE datePosted = %s GROUP BY seller
            ) as temp
        );
        """
        self.execute_and_display(sql, (date_str, date_str), "User | Items Posted")

    def execute_and_display(self, query, params, headers):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if not rows:
                self.q_results.setText("No results found.")
            else:
                result_text = f"<b>{headers}</b><br>"
                for row in rows:
                    result_text += " | ".join(str(val) for val in row) + "<br>"
                self.q_results.setText(result_text)

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            self.q_results.setText(f"<span style='color:red;'>Error: {err.msg}</span>")