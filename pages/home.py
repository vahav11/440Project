from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class HomePage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        welcome = QLabel("Hi, sign in to get started")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.signin_button = QPushButton("Sign In")
        self.signup_button = QPushButton("Sign Up")

        layout.addWidget(welcome)
        layout.addWidget(self.signin_button)
        layout.addWidget(self.signup_button)

        self.setLayout(layout)