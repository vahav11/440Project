import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QCheckBox)
from werkzeug.security import generate_password_hash
from pages.keynav import KeyNavMixin
import mysql.connector
import db


class SignupPage(KeyNavMixin, QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Create an Account"))

        form = QFormLayout()

        self.username = QLineEdit()
        self.firstName = QLineEdit()
        self.lastName = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.password = QLineEdit()
        self.confirm = QLineEdit()

        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.phone.setPlaceholderText("(818) 555-1234")

        form.addRow("Username:", self.username)
        form.addRow("First Name:", self.firstName)
        form.addRow("Last Name:", self.lastName)
        form.addRow("Email:", self.email)
        form.addRow("Phone:", self.phone)
        form.addRow("Password:", self.password)
        form.addRow("Confirm Password:", self.confirm)

        layout.addLayout(form)

        self.show_password = QCheckBox("Show password")
        self.show_password.stateChanged.connect(self.toggle_password)
        layout.addWidget(self.show_password)

        rules = QLabel(
            "Password rules: at least 8 characters, and must include "
            "an uppercase letter, a lowercase letter, and a number."
        )
        rules.setWordWrap(True)
        rules.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(rules)

        self.message = QLabel("")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        self.create_button = QPushButton("Create Account")
        self.back_button = QPushButton("Back")
        layout.addWidget(self.create_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.setup_key_navigation(
            [self.username, self.firstName, self.lastName, self.email,
             self.phone, self.password, self.confirm],
            self.create_button
        )

    def toggle_password(self):
        if self.show_password.isChecked():
            mode = QLineEdit.EchoMode.Normal
        else:
            mode = QLineEdit.EchoMode.Password
        self.password.setEchoMode(mode)
        self.confirm.setEchoMode(mode)

    def show_error(self, text):
        self.message.setStyleSheet("color: red;")
        self.message.setText(text)
        return False

    def attempt_signup(self):

        username = self.username.text().strip().lower()
        firstName = self.firstName.text().strip()
        lastName = self.lastName.text().strip()
        email = self.email.text().strip().lower()
        phone = "".join(c for c in self.phone.text() if c.isdigit())
        password = self.password.text()
        confirm = self.confirm.text()

        # --- format checks ---

        if not re.fullmatch(r"[a-z0-9_]{3,20}", username):
            return self.show_error("Username must be 3-20 characters: letters, numbers, underscore. No spaces.")

        if not firstName or not lastName:
            return self.show_error("First and last name are required.")

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email):
            return self.show_error("Please enter a valid email address.")

        if len(phone) != 10:
            return self.show_error("Phone must contain 10 digits.")

        if len(password) < 8:
            return self.show_error("Password must be at least 8 characters.")

        if not re.search(r"[A-Z]", password):
            return self.show_error("Password must contain an uppercase letter.")

        if not re.search(r"[a-z]", password):
            return self.show_error("Password must contain a lowercase letter.")

        if not re.search(r"[0-9]", password):
            return self.show_error("Password must contain a number.")

        if password != confirm:
            return self.show_error("Passwords do not match.")

        # --- duplicate checks and save ---

        conn = None
        cursor = None

        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT username FROM user WHERE username = %s", (username,))
            if cursor.fetchone():
                return self.show_error("That username is already taken.")

            cursor.execute("SELECT username FROM user WHERE email = %s", (email,))
            if cursor.fetchone():
                return self.show_error("That email is already registered.")

            cursor.execute("SELECT username FROM user WHERE phone = %s", (phone,))
            if cursor.fetchone():
                return self.show_error("That phone number is already registered.")

            hashed = generate_password_hash(password)

            cursor.execute(
                "INSERT INTO user (username, password, firstName, lastName, email, phone) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (username, hashed, firstName, lastName, email, phone)
            )

            conn.commit()

        except mysql.connector.Error as err:
            return self.show_error(
                "Could not reach the database. Check that MySQL is running "
                f"and that config.py is correct.\n\nDetails: {err}"
            )

        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None and conn.is_connected():
                conn.close()

        self.clear_form()
        return True

    def clear_form(self):
        for box in [self.username, self.firstName, self.lastName,
                    self.email, self.phone, self.password, self.confirm]:
            box.clear()
        self.message.setText("")