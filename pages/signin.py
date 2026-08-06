from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QCheckBox)
from werkzeug.security import check_password_hash
from pages.keynav import KeyNavMixin
import mysql.connector
import db


class SigninPage(KeyNavMixin, QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Sign In"))

        form = QFormLayout()

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Username:", self.username)
        form.addRow("Password:", self.password)

        layout.addLayout(form)

        self.show_password = QCheckBox("Show password")
        self.show_password.stateChanged.connect(self.toggle_password)
        layout.addWidget(self.show_password)

        self.message = QLabel("")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        self.signin_button = QPushButton("Sign In")
        self.goto_signup_button = QPushButton("Don't have an account? Sign Up")
        self.back_button = QPushButton("Back")

        layout.addWidget(self.signin_button)
        layout.addWidget(self.goto_signup_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.setup_key_navigation(
            [self.username, self.password],
            self.signin_button
        )

    def toggle_password(self):
        if self.show_password.isChecked():
            self.password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password.setEchoMode(QLineEdit.EchoMode.Password)

    def show_error(self, text):
        self.message.setStyleSheet("color: red;")
        self.message.setText(text)
        return None

    def attempt_signin(self):

        username = self.username.text().strip().lower()
        password = self.password.text()

        if not username or not password:
            return self.show_error("Please enter your username and password.")

        conn = None
        cursor = None

        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT username, password, firstName, lastName FROM user WHERE username = %s",
                (username,)
            )
            row = cursor.fetchone()

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

        if row is None:
            return self.show_error("Incorrect username or password.")

        stored_hash = row[1]
        firstName = row[2]
        lastName = row[3]

        if not check_password_hash(stored_hash, password):
            return self.show_error("Incorrect username or password.")

        self.username.clear()
        self.password.clear()
        self.message.setText("")

        return (firstName, lastName)