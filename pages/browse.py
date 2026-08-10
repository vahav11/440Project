from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QScrollArea, QFrame)
import mysql.connector
import db


class BrowsePage(QWidget):

    def __init__(self):
        super().__init__()

        # main.py sets this to a function that opens the item detail page
        self.on_open_item = None

        layout = QVBoxLayout()

        title = QLabel("Browse Items")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.message = QLabel("")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        middle = QHBoxLayout()

        left = QVBoxLayout()
        left.addWidget(QLabel("Categories"))
        self.category_list = QListWidget()
        self.category_list.setMaximumWidth(180)
        self.category_list.currentTextChanged.connect(self.load_items)
        left.addWidget(self.category_list)
        middle.addLayout(left)

        self.cards_area = QVBoxLayout()
        self.cards_area.addStretch()

        holder = QWidget()
        holder.setLayout(self.cards_area)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(holder)
        middle.addWidget(scroll)

        layout.addLayout(middle)

        self.refresh_button = QPushButton("Refresh")
        self.back_button = QPushButton("Back")
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.back_button)

        self.refresh_button.clicked.connect(self.load_categories)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    # Load the list of categories that actually exist in the database
    # ------------------------------------------------------------------
    def load_categories(self):
        self.message.setText("")
        self.category_list.clear()
        self.category_list.addItem("All")

        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT category FROM item_category ORDER BY category"
            )
            for row in cursor.fetchall():
                self.category_list.addItem(row[0])
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            self.message.setStyleSheet("color: red;")
            self.message.setText(f"Could not load categories. {err}")
            return

        self.category_list.setCurrentRow(0)

    # ------------------------------------------------------------------
    # Load the items for whichever category is selected
    # ------------------------------------------------------------------
    def load_items(self, category):
        self.clear_cards()

        if not category:
            return

        if category == "All":
            sql = ("SELECT itemID, title, description, price, seller, datePosted "
                   "FROM item ORDER BY datePosted DESC, itemID DESC")
            params = ()
        else:
            sql = ("SELECT i.itemID, i.title, i.description, i.price, "
                   "       i.seller, i.datePosted "
                   "FROM item i "
                   "JOIN item_category c ON i.itemID = c.itemID "
                   "WHERE c.category = %s "
                   "ORDER BY i.datePosted DESC, i.itemID DESC")
            params = (category,)

        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            self.message.setStyleSheet("color: red;")
            self.message.setText(f"Could not load items. {err}")
            return

        if not rows:
            empty = QLabel("No items in this category yet.")
            empty.setStyleSheet("color: gray;")
            self.cards_area.insertWidget(self.cards_area.count() - 1, empty)
            return

        for row in rows:
            card = self.make_card(row)
            self.cards_area.insertWidget(self.cards_area.count() - 1, card)

    # ------------------------------------------------------------------
    # Build one card for one item
    # ------------------------------------------------------------------
    def make_card(self, row):
        itemID, item_title, description, price, seller, datePosted = row

        card = QFrame()
        card.setFrameShape(QFrame.Shape.Box)
        card.setStyleSheet(
            "QFrame { border: 1px solid gray; border-radius: 6px; padding: 8px; }"
        )

        box = QVBoxLayout()

        heading = QLabel(f"{item_title}   —   ${price}")
        heading.setStyleSheet("font-weight: bold; border: none;")
        box.addWidget(heading)

        details = QLabel(f"Item #{itemID}   ·   posted by {seller}   ·   {datePosted}")
        details.setStyleSheet("color: gray; border: none;")
        box.addWidget(details)

        if description:
            desc = QLabel(description)
            desc.setWordWrap(True)
            desc.setStyleSheet("border: none;")
            box.addWidget(desc)

        open_button = QPushButton("Reviews")
        open_button.setStyleSheet("border: 1px solid gray; padding: 4px;")
        open_button.clicked.connect(
            lambda _, i=itemID: self.on_open_item(i) if self.on_open_item else None
        )
        box.addWidget(open_button)

        card.setLayout(box)
        return card

    # ------------------------------------------------------------------
    def clear_cards(self):
        while self.cards_area.count() > 1:
            item = self.cards_area.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
