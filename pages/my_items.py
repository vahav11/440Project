from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFrame, QScrollArea,
                             QMessageBox)
import mysql.connector
import db
import session


class MyItemsPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("My Items")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.message = QLabel("")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        self.cards_area = QVBoxLayout()
        self.cards_area.addStretch()

        holder = QWidget()
        holder.setLayout(self.cards_area)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(holder)
        layout.addWidget(scroll)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_items)
        layout.addWidget(self.refresh_button)

        self.back_button = QPushButton("Back")
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def show_error(self, text):
        self.message.setStyleSheet("color: red;")
        self.message.setText(text)

    def show_success(self, text):
        self.message.setStyleSheet("color: green;")
        self.message.setText(text)

    def load_items(self):
        self.clear_cards()

        if not session.current_user:
            self.show_error("You are not signed in.")
            return

        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT itemID, title, description, price, datePosted "
                "FROM item WHERE seller = %s "
                "ORDER BY datePosted DESC, itemID DESC",
                (session.current_user,)
            )
            items = cursor.fetchall()

            categories = {}
            for itemID, *_ in items:
                cursor.execute(
                    "SELECT category FROM item_category WHERE itemID = %s "
                    "ORDER BY category",
                    (itemID,)
                )
                categories[itemID] = [r[0] for r in cursor.fetchall()]

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_error(f"Could not load your items. {err.msg}")
            return

        if not items:
            empty = QLabel("You have not posted any items yet.")
            empty.setStyleSheet("color: gray;")
            self.cards_area.insertWidget(self.cards_area.count() - 1, empty)
            return

        for row in items:
            card = self.make_card(row, categories[row[0]])
            self.cards_area.insertWidget(self.cards_area.count() - 1, card)

    def make_card(self, row, cats):
        itemID, item_title, description, price, datePosted = row

        card = QFrame()
        card.setFrameShape(QFrame.Shape.Box)
        card.setStyleSheet(
            "QFrame { border: 1px solid gray; border-radius: 6px; padding: 8px; }"
            "QLabel { border: none; }"
        )

        box = QVBoxLayout()

        heading = QLabel(f"{item_title}    ${price}")
        heading.setStyleSheet("font-weight: bold;")
        box.addWidget(heading)

        details = QLabel(f"Item #{itemID}    posted {datePosted}")
        details.setStyleSheet("color: gray;")
        box.addWidget(details)

        if description:
            desc = QLabel(description)
            desc.setWordWrap(True)
            box.addWidget(desc)

        cat_label = QLabel("Categories: " + (", ".join(cats) if cats else "none"))
        cat_label.setWordWrap(True)
        box.addWidget(cat_label)

        # price
        price_row = QHBoxLayout()
        price_box = QLineEdit()
        price_box.setPlaceholderText("new price")
        price_button = QPushButton("Update Price")
        price_button.clicked.connect(
            lambda _, i=itemID, b=price_box: self.update_price(i, b)
        )
        price_row.addWidget(price_box)
        price_row.addWidget(price_button)
        box.addLayout(price_row)

        # categories
        cat_row = QHBoxLayout()
        cat_box = QLineEdit()
        cat_box.setPlaceholderText("category")
        add_button = QPushButton("Add Category")
        add_button.clicked.connect(
            lambda _, i=itemID, b=cat_box: self.add_category(i, b)
        )
        remove_button = QPushButton("Remove Category")
        remove_button.clicked.connect(
            lambda _, i=itemID, b=cat_box: self.remove_category(i, b)
        )
        cat_row.addWidget(cat_box)
        cat_row.addWidget(add_button)
        cat_row.addWidget(remove_button)
        box.addLayout(cat_row)

        delete_button = QPushButton("Delete Item")
        delete_button.clicked.connect(lambda _, i=itemID: self.delete_item(i))
        box.addWidget(delete_button)

        card.setLayout(box)
        return card

    def update_price(self, itemID, box):
        text = box.text().strip()

        try:
            price = float(text)
        except ValueError:
            self.show_error("Price must be a number, for example 19.99")
            return

        if price < 0:
            self.show_error("Price cannot be negative.")
            return

        if self.run_change(
            "UPDATE item SET price = %s WHERE itemID = %s AND seller = %s",
            (price, itemID, session.current_user)
        ):
            self.show_success(f"Item #{itemID} price updated.")
            self.load_items()

    def add_category(self, itemID, box):
        word = box.text().strip().lower()

        if not word:
            self.show_error("Type a category first.")
            return
        if " " in word:
            self.show_error("A category must be a single word.")
            return

        if self.run_change(
            "INSERT INTO item_category (itemID, category) VALUES (%s, %s)",
            (itemID, word),
            duplicate_message=f"Item #{itemID} already has the category '{word}'."
        ):
            self.show_success(f"Added '{word}' to item #{itemID}.")
            self.load_items()

    def remove_category(self, itemID, box):
        word = box.text().strip().lower()

        if not word:
            self.show_error("Type a category first.")
            return

        if self.run_change(
            "DELETE FROM item_category WHERE itemID = %s AND category = %s",
            (itemID, word),
            empty_message=f"Item #{itemID} does not have the category '{word}'."
        ):
            self.show_success(f"Removed '{word}' from item #{itemID}.")
            self.load_items()

    def delete_item(self, itemID):
        confirm = QMessageBox.question(
            self, "Delete item",
            f"Delete item #{itemID}? Its categories and reviews will go too.\n"
            "This cannot be undone."
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        if self.run_change(
            "DELETE FROM item WHERE itemID = %s AND seller = %s",
            (itemID, session.current_user)
        ):
            self.show_success(f"Item #{itemID} deleted.")
            self.load_items()

    # runs one statement. rowcount 0 means nothing matched, usually
    # because the item isnt ours
    def run_change(self, sql, params, duplicate_message=None, empty_message=None):
        conn = None
        cursor = None
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)

            if cursor.rowcount == 0:
                conn.rollback()
                self.show_error(empty_message or "Nothing was changed.")
                return False

            conn.commit()
            return True

        except mysql.connector.Error as err:
            if conn is not None:
                conn.rollback()
            if err.errno == 1062 and duplicate_message:
                self.show_error(duplicate_message)
            else:
                self.show_error(err.msg)
            return False

        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None and conn.is_connected():
                conn.close()

    def clear_cards(self):
        self.message.setText("")
        while self.cards_area.count() > 1:
            old = self.cards_area.takeAt(0)
            w = old.widget()
            if w is not None:
                w.deleteLater()
