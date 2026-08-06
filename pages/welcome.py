from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class WelcomePage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.greeting = QLabel("")
        self.greeting.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logout_button = QPushButton("Log Out")

        layout.addWidget(self.greeting)
        layout.addWidget(self.logout_button)

        self.setLayout(layout)