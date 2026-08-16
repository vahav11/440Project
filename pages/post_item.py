from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QTextEdit, QPushButton)
from datetime import date
import mysql.connector
import db
import session


class PostItemPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("Post a New Item")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()

        self.title_box = QLineEdit()
        self.title_box.setMaxLength(100)

        self.description_box = QTextEdit()
        self.description_box.setFixedHeight(70)

        self.price_box = QLineEdit()
        self.price_box.setPlaceholderText("19.99")

        self.categories_box = QLineEdit()
        self.categories_box.setPlaceholderText("electronics, books, gaming")

        form.addRow("Title:", self.title_box)
        form.addRow("Description:", self.description_box)
        form.addRow("Price ($):", self.price_box)
        form.addRow("Categories:", self.categories_box)

        layout.addLayout(form)

        hint = QLabel("Separate categories with commas. One word each, no spaces.")
        hint.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(hint)

        self.message = QLabel("")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        self.post_button = QPushButton("Post Item")
        self.post_button.clicked.connect(self.post_item)
        layout.addWidget(self.post_button)

        self.back_button = QPushButton("Back")
        layout.addWidget(self.back_button)

        layout.addStretch()
        self.setLayout(layout)

    def show_error(self, text):
        self.message.setStyleSheet("color: red;")
        self.message.setText(text)

    def show_success(self, text):
        self.message.setStyleSheet("color: green;")
        self.message.setText(text)

    def clear_form(self):
        self.title_box.clear()
        self.description_box.clear()
        self.price_box.clear()
        self.categories_box.clear()

    def post_item(self):

        title = self.title_box.text().strip()
        description = self.description_box.toPlainText().strip()
        price_text = self.price_box.text().strip()
        category_text = self.categories_box.text().strip()

        if not title:
            self.show_error("Please enter a title.")
            return

        try:
            price = float(price_text)
        except ValueError:
            self.show_error("Price must be a number, for example 19.99")
            return

        if price < 0:
            self.show_error("Price cannot be negative.")
            return

        # split on commas, lowercase, skip blanks and repeats
        categories = []
        for piece in category_text.split(","):
            word = piece.strip().lower()
            if word and word not in categories:
                categories.append(word)

        if not categories:
            self.show_error("Please enter at least one category.")
            return

        for word in categories:
            if " " in word:
                self.show_error(f"'{word}' is not one word. Categories must be single words.")
                return

        # item first, then its categories, one commit at the end so we
        # dont end up with an item that lost half its categories
        conn = None
        cursor = None
        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO item (title, description, price, datePosted, seller) "
                "VALUES (%s, %s, %s, %s, %s)",
                (title, description, price, date.today(), session.current_user)
            )

            new_id = cursor.lastrowid   # the id mysql just made

            for word in categories:
                cursor.execute(
                    "INSERT INTO item_category (itemID, category) VALUES (%s, %s)",
                    (new_id, word)
                )

            conn.commit()

        except mysql.connector.Error as err:
            if conn is not None:
                conn.rollback()
            self.show_error(err.msg)
            return

        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None and conn.is_connected():
                conn.close()

        self.clear_form()
        self.show_success(f"Item #{new_id} posted.")
