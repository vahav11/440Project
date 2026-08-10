from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class WelcomePage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.greeting = QLabel("")
        self.greeting.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.greeting.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.greeting)

        layout.addSpacing(15)

        menu = QLabel("What would you like to do?")
        menu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(menu)

        layout.addSpacing(10)

        self.post_item_button = QPushButton("Post a New Item")
        self.my_items_button = QPushButton("My Items")
        self.browse_button = QPushButton("Browse Items")

        layout.addWidget(self.post_item_button)
        layout.addWidget(self.my_items_button)
        layout.addWidget(self.browse_button)

        layout.addSpacing(20)

        self.logout_button = QPushButton("Log Out")
        layout.addWidget(self.logout_button)

        layout.addSpacing(25)

        self.queries_button = QPushButton("Store Reports")
        self.queries_button.setStyleSheet("color: gray;")
        layout.addWidget(self.queries_button)

        layout.addStretch()

        self.setLayout(layout)
