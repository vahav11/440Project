from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView)


class ReviewPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("Write a Review")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Choose an item to review:"))

        self.item_table = QTableWidget()
        self.item_table.setColumnCount(5)
        self.item_table.setHorizontalHeaderLabels(
            ["Item ID", "Title", "Price", "Seller", "Posted"]
        )
        self.item_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.item_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.item_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.item_table)

        rating_row = QHBoxLayout()
        rating_row.addWidget(QLabel("Rating:"))
        self.rating = QComboBox()
        self.rating.addItems(["Excellent", "Good", "Fair", "Poor"])
        rating_row.addWidget(self.rating)
        rating_row.addStretch()
        layout.addLayout(rating_row)

        layout.addWidget(QLabel("Comment:"))
        self.comment = QLineEdit()
        self.comment.setMaxLength(255)
        self.comment.setPlaceholderText("A short comment (up to 255 characters)")
        layout.addWidget(self.comment)

        self.message = QLabel("")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        self.submit_button = QPushButton("Submit Review")
        self.refresh_button = QPushButton("Refresh List")
        self.back_button = QPushButton("Back")

        layout.addWidget(self.submit_button)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def show_error(self, text):
        self.message.setStyleSheet("color: red;")
        self.message.setText(text)
        return False

    def show_success(self, text):
        self.message.setStyleSheet("color: green;")
        self.message.setText(text)
        return True
