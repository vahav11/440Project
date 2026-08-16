from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QDateEdit, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView)
from PyQt6.QtCore import QDate
import mysql.connector
import db


# most expensive item in each category.
# compare each item's price to the max price inside its own category.
# using = instead of sorting is what makes ties come back too.
Q1 = """
SELECT   c.category, i.title, i.price, i.seller
FROM     item_category c
JOIN     item i ON c.itemID = i.itemID
WHERE    i.price = (SELECT MAX(i2.price)
                    FROM   item_category c2
                    JOIN   item i2 ON c2.itemID = i2.itemID
                    WHERE  c2.category = c.category)
ORDER BY c.category, i.title
"""

# users who posted 2 items on one day, one in X and one in Y.
# item joined to itself. same seller, same date.
# i1.itemID <> i2.itemID keeps it from matching an item with itself.
Q2 = """
SELECT DISTINCT i1.seller, i1.datePosted
FROM   item i1
JOIN   item_category c1 ON i1.itemID = c1.itemID
JOIN   item i2 ON i1.seller = i2.seller
              AND i1.datePosted = i2.datePosted
JOIN   item_category c2 ON i2.itemID = c2.itemID
WHERE  i1.itemID <> i2.itemID
  AND  c1.category = %s
  AND  c2.category = %s
ORDER BY i1.seller
"""

# items of one user where every review is Excellent or Good.
# two parts to this one:
#   EXISTS      -> has to have at least one review
#   NOT EXISTS  -> and none of them can be Fair or Poor
# without the EXISTS, items with no reviews would sneak in.
Q3 = """
SELECT   i.itemID, i.title, i.price, i.datePosted
FROM     item i
WHERE    i.seller = %s
  AND    EXISTS (SELECT *
                 FROM   review r
                 WHERE  r.itemID = i.itemID)
  AND    NOT EXISTS (SELECT *
                     FROM   review r
                     WHERE  r.itemID = i.itemID
                       AND  r.rating NOT IN ('Excellent', 'Good'))
ORDER BY i.itemID
"""

# who posted the most items on a given date.
# HAVING count = the max count, so ties all come back.
Q4 = """
SELECT   seller, COUNT(*) AS items_posted
FROM     item
WHERE    datePosted = %s
GROUP BY seller
HAVING   COUNT(*) = (SELECT MAX(c)
                     FROM (SELECT COUNT(*) AS c
                           FROM   item
                           WHERE  datePosted = %s
                           GROUP BY seller) AS counts)
ORDER BY seller
"""

# users whose reviews are all Poor.
# reading FROM review already means they wrote at least one,
# so only the NOT EXISTS half is needed here.
Q5 = """
SELECT   DISTINCT r.reviewer
FROM     review r
WHERE    NOT EXISTS (SELECT *
                     FROM   review r2
                     WHERE  r2.reviewer = r.reviewer
                       AND  r2.rating <> 'Poor')
ORDER BY r.reviewer
"""

# users whose items never got a Poor review.
# items with no reviews still count as fine, and thats automatic here.
# an item with no reviews never shows up in the inner query, so it
# cant disqualify anybody. a join would have dropped those items.
Q6 = """
SELECT   DISTINCT i.seller
FROM     item i
WHERE    NOT EXISTS (SELECT *
                     FROM   item i2
                     JOIN   review r ON i2.itemID = r.itemID
                     WHERE  i2.seller = i.seller
                       AND  r.rating = 'Poor')
ORDER BY i.seller
"""


class ReportsPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("Store Reports")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.tabs = QTabWidget()

        self.tabs.addTab(self.build_q1(), "Q1")
        self.tabs.addTab(self.build_q2(), "Q2")
        self.tabs.addTab(self.build_q3(), "Q3")
        self.tabs.addTab(self.build_q4(), "Q4")
        self.tabs.addTab(self.build_q5(), "Q5")
        self.tabs.addTab(self.build_q6(), "Q6")

        layout.addWidget(self.tabs)

        self.refresh_button = QPushButton("Reload category and user lists")
        self.refresh_button.clicked.connect(self.load_choices)
        layout.addWidget(self.refresh_button)

        self.back_button = QPushButton("Back")
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    # every tab is the same shape, description then inputs then a run
    # button then a table
    def new_tab(self, description):
        page = QWidget()
        box = QVBoxLayout()

        label = QLabel(description)
        label.setWordWrap(True)
        box.addWidget(label)

        page.setLayout(box)
        return page, box

    def finish_tab(self, box, run_text, handler):
        button = QPushButton(run_text)
        button.clicked.connect(handler)
        box.addWidget(button)

        table = QTableWidget()
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        box.addWidget(table)

        message = QLabel("")
        message.setWordWrap(True)
        box.addWidget(message)

        return table, message

    def build_q1(self):
        page, box = self.new_tab(
            "<b>Q1:</b> the most expensive item or items in each category. "
            "If several items share the highest price, all of them show up.")
        self.q1_table, self.q1_message = self.finish_tab(box, "Run Q1", self.run_q1)
        return page

    def run_q1(self):
        self.run(Q1, (), ["Category", "Title", "Price", "Seller"],
                 self.q1_table, self.q1_message)

    def build_q2(self):
        page, box = self.new_tab(
            "<b>Q2:</b> users who posted at least two different items on the "
            "same day, where one item is in category X and the other is in "
            "category Y.")

        row = QHBoxLayout()
        row.addWidget(QLabel("Category X:"))
        self.q2_x = QComboBox()
        self.q2_x.setEditable(True)
        row.addWidget(self.q2_x)
        row.addWidget(QLabel("Category Y:"))
        self.q2_y = QComboBox()
        self.q2_y.setEditable(True)
        row.addWidget(self.q2_y)
        box.addLayout(row)

        self.q2_table, self.q2_message = self.finish_tab(box, "Run Q2", self.run_q2)
        return page

    def run_q2(self):
        x = self.q2_x.currentText().strip().lower()
        y = self.q2_y.currentText().strip().lower()

        if not x or not y:
            self.q2_message.setStyleSheet("color: red;")
            self.q2_message.setText("Please give both categories.")
            return

        self.run(Q2, (x, y), ["User", "Date Posted"],
                 self.q2_table, self.q2_message)

    def build_q3(self):
        page, box = self.new_tab(
            "<b>Q3:</b> items posted by one user where the item has at least "
            "one review, and every review for it is Excellent or Good.")

        row = QHBoxLayout()
        row.addWidget(QLabel("User:"))
        self.q3_user = QComboBox()
        self.q3_user.setEditable(True)
        row.addWidget(self.q3_user)
        box.addLayout(row)

        self.q3_table, self.q3_message = self.finish_tab(box, "Run Q3", self.run_q3)
        return page

    def run_q3(self):
        username = self.q3_user.currentText().strip().lower()

        if not username:
            self.q3_message.setStyleSheet("color: red;")
            self.q3_message.setText("Please give a username.")
            return

        self.run(Q3, (username,), ["Item ID", "Title", "Price", "Date Posted"],
                 self.q3_table, self.q3_message)

    def build_q4(self):
        page, box = self.new_tab(
            "<b>Q4:</b> the user or users who posted the largest number of "
            "items on a given date. If there is a tie, all of them show up.")

        row = QHBoxLayout()
        row.addWidget(QLabel("Date:"))
        self.q4_date = QDateEdit()
        self.q4_date.setCalendarPopup(True)
        self.q4_date.setDisplayFormat("yyyy-MM-dd")
        self.q4_date.setDate(QDate.currentDate())
        row.addWidget(self.q4_date)
        row.addStretch()
        box.addLayout(row)

        self.q4_table, self.q4_message = self.finish_tab(box, "Run Q4", self.run_q4)
        return page

    def run_q4(self):
        chosen = self.q4_date.date().toString("yyyy-MM-dd")
        self.run(Q4, (chosen, chosen), ["User", "Items Posted"],
                 self.q4_table, self.q4_message)

    def build_q5(self):
        page, box = self.new_tab(
            "<b>Q5:</b> users who have written one or more reviews, where "
            "every review they wrote is rated Poor.")
        self.q5_table, self.q5_message = self.finish_tab(box, "Run Q5", self.run_q5)
        return page

    def run_q5(self):
        self.run(Q5, (), ["User"], self.q5_table, self.q5_message)

    def build_q6(self):
        page, box = self.new_tab(
            "<b>Q6:</b> users whose posted items have never received a Poor "
            "review. Items with no reviews still count as passing.")
        self.q6_table, self.q6_message = self.finish_tab(box, "Run Q6", self.run_q6)
        return page

    def run_q6(self):
        self.run(Q6, (), ["User"], self.q6_table, self.q6_message)

    # fills the dropdowns from whats actually in the database so nothing
    # is hardcoded
    def load_choices(self):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT DISTINCT category FROM item_category "
                           "ORDER BY category")
            categories = [r[0] for r in cursor.fetchall()]

            cursor.execute("SELECT username FROM user ORDER BY username")
            users = [r[0] for r in cursor.fetchall()]

            cursor.close()
            conn.close()
        except mysql.connector.Error:
            return

        for combo in (self.q2_x, self.q2_y):
            current = combo.currentText()
            combo.clear()
            combo.addItems(categories)
            combo.setCurrentText(current)

        current = self.q3_user.currentText()
        self.q3_user.clear()
        self.q3_user.addItems(users)
        self.q3_user.setCurrentText(current)

    # one runner for all six, just gets handed a different table
    def run(self, sql, params, headers, table, message):
        conn = None
        cursor = None
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        except mysql.connector.Error as err:
            message.setStyleSheet("color: red;")
            message.setText(f"Database error: {err.msg}")
            return
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None and conn.is_connected():
                conn.close()

        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                table.setItem(r, c, QTableWidgetItem(str(value)))

        message.setStyleSheet("color: gray;")
        message.setText(f"{len(rows)} row(s) returned.")
