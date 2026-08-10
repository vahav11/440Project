from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QFrame,
                             QScrollArea)
from datetime import date
import mysql.connector
import db
import session

RATINGS = ["Excellent", "Good", "Fair", "Poor"]


class ItemDetailPage(QWidget):

    def __init__(self):
        super().__init__()

        self.itemID = None
        self.seller = None

        layout = QVBoxLayout()

        self.title_label = QLabel("")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.details_label = QLabel("")
        self.details_label.setStyleSheet("color: gray;")
        layout.addWidget(self.details_label)

        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        self.categories_label = QLabel("")
        self.categories_label.setWordWrap(True)
        layout.addWidget(self.categories_label)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Ratings"))
        self.rating_counts = QLabel("")
        self.rating_counts.setStyleSheet("font-family: Consolas, monospace;")
        layout.addWidget(self.rating_counts)

        layout.addSpacing(10)

        self.reviews_heading = QLabel("Reviews")
        layout.addWidget(self.reviews_heading)

        self.reviews_area = QVBoxLayout()
        self.reviews_area.addStretch()
        holder = QWidget()
        holder.setLayout(self.reviews_area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(holder)
        layout.addWidget(scroll)

        self.form = QWidget()
        form_box = QVBoxLayout()

        form_box.addWidget(QLabel("Write a review"))

        rating_row = QHBoxLayout()
        rating_row.addWidget(QLabel("Rating:"))
        self.rating = QComboBox()
        self.rating.addItems(RATINGS)
        rating_row.addWidget(self.rating)
        rating_row.addStretch()
        form_box.addLayout(rating_row)

        self.comment = QLineEdit()
        self.comment.setMaxLength(255)
        self.comment.setPlaceholderText("A short comment (up to 255 characters)")
        form_box.addWidget(self.comment)

        self.submit_button = QPushButton("Submit Review")
        self.submit_button.clicked.connect(self.submit_review)
        form_box.addWidget(self.submit_button)

        self.form.setLayout(form_box)
        layout.addWidget(self.form)

        self.message = QLabel("")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        self.back_button = QPushButton("Back to Browse")
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    def show_error(self, text):
        self.message.setStyleSheet("color: red;")
        self.message.setText(text)

    def show_success(self, text):
        self.message.setStyleSheet("color: green;")
        self.message.setText(text)

    # ------------------------------------------------------------------
    # Load one item and everything about it
    # ------------------------------------------------------------------
    def load_item(self, itemID):
        self.itemID = itemID
        self.message.setText("")
        self.comment.clear()

        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT title, description, price, seller, datePosted "
                "FROM item WHERE itemID = %s",
                (itemID,)
            )
            row = cursor.fetchone()

            if row is None:
                cursor.close()
                conn.close()
                self.show_error("That item no longer exists.")
                return

            item_title, description, price, seller, datePosted = row
            self.seller = seller

            cursor.execute(
                "SELECT category FROM item_category WHERE itemID = %s "
                "ORDER BY category",
                (itemID,)
            )
            categories = [r[0] for r in cursor.fetchall()]

            cursor.execute(
                "SELECT rating, COUNT(*) FROM review WHERE itemID = %s "
                "GROUP BY rating",
                (itemID,)
            )
            counts = {r[0]: r[1] for r in cursor.fetchall()}

            cursor.execute(
                "SELECT reviewer, rating, comment, reviewDate FROM review "
                "WHERE itemID = %s ORDER BY reviewDate DESC, reviewID DESC",
                (itemID,)
            )
            reviews = cursor.fetchall()

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_error(f"Could not load this item. {err}")
            return

        self.title_label.setText(f"{item_title}   —   ${price}")
        self.details_label.setText(
            f"Item #{itemID}   ·   posted by {seller}   ·   {datePosted}"
        )
        self.description_label.setText(description or "")

        if categories:
            self.categories_label.setText("Categories: " + ", ".join(categories))
        else:
            self.categories_label.setText("Categories: none")

        lines = []
        total = 0
        for name in RATINGS:
            n = counts.get(name, 0)
            total += n
            lines.append(f"{name:<12}{'.' * 10} {n}")
        self.rating_counts.setText("\n".join(lines))

        self.reviews_heading.setText(f"Reviews ({total})")

        self.fill_reviews(reviews)
        self.update_form_visibility()

    # ------------------------------------------------------------------
    def fill_reviews(self, reviews):
        while self.reviews_area.count() > 1:
            old = self.reviews_area.takeAt(0)
            w = old.widget()
            if w is not None:
                w.deleteLater()

        if not reviews:
            empty = QLabel("No reviews yet.")
            empty.setStyleSheet("color: gray;")
            self.reviews_area.insertWidget(self.reviews_area.count() - 1, empty)
            return

        for reviewer, rating, comment, reviewDate in reviews:
            card = QFrame()
            card.setFrameShape(QFrame.Shape.Box)
            card.setStyleSheet(
                "QFrame { border: 1px solid gray; border-radius: 5px; padding: 6px; }"
            )
            box = QVBoxLayout()

            head = QLabel(f"{rating}   ·   {reviewer}   ·   {reviewDate}")
            head.setStyleSheet("font-weight: bold; border: none;")
            box.addWidget(head)

            if comment:
                body = QLabel(comment)
                body.setWordWrap(True)
                body.setStyleSheet("border: none;")
                box.addWidget(body)

            card.setLayout(box)
            self.reviews_area.insertWidget(self.reviews_area.count() - 1, card)

    # ------------------------------------------------------------------
    # Hide the form when the user should not be able to review this item
    # ------------------------------------------------------------------
    def update_form_visibility(self):
        if session.current_user is None:
            self.form.hide()
            return

        if self.seller == session.current_user:
            self.form.hide()
            self.show_error("This is your own item, so you cannot review it.")
            return

        self.form.show()

    # ------------------------------------------------------------------
    def submit_review(self):
        comment = self.comment.text().strip()
        rating = self.rating.currentText()

        if not comment:
            self.show_error("Please write a short comment.")
            return

        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO review (itemID, reviewer, rating, comment, reviewDate) "
                "VALUES (%s, %s, %s, %s, %s)",
                (self.itemID, session.current_user, rating, comment, date.today())
            )
            conn.commit()
            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            if err.errno == 1062:
                self.show_error("You have already reviewed this item.")
            else:
                self.show_error(str(err.msg))
            return

        self.load_item(self.itemID)
        self.show_success("Review submitted.")
