from PyQt6.QtWidgets import QApplication, QStackedWidget
from pages.home import HomePage
from pages.signup import SignupPage
from pages.signin import SigninPage
from pages.welcome import WelcomePage
from pages.browse import BrowsePage
from pages.item_detail import ItemDetailPage
from pages.item_manager import ItemManagerPage
import sys
import db
import session

# Ask for the MySQL password before the window opens, so the terminal
# is not waiting for input while the app is already on screen.
db.get_password()

app = QApplication(sys.argv)

stack = QStackedWidget()
stack.setWindowTitle("COMP 440")
stack.resize(600, 500)

home = HomePage()
signup = SignupPage()
signin = SigninPage()
welcome = WelcomePage()
browse = BrowsePage()
item_detail = ItemDetailPage()
item_manager = ItemManagerPage()

stack.addWidget(home)        # 0
stack.addWidget(signup)      # 1
stack.addWidget(signin)      # 2
stack.addWidget(welcome)     # 3
stack.addWidget(browse)      # 4
stack.addWidget(item_detail) # 5
stack.addWidget(item_manager)# 6


def do_signup():
    if signup.attempt_signup():
        signin.message.setStyleSheet("color: green;")
        signin.message.setText("Account created. Please sign in.")
        stack.setCurrentIndex(2)


def do_signin():
    result = signin.attempt_signin()
    if result:
        username, firstName, lastName = result
        session.current_user = username
        welcome.greeting.setText(f"Welcome, {firstName} {lastName}")
        stack.setCurrentIndex(3)


# --- Navigation Mapping ---
home.signup_button.clicked.connect(lambda: stack.setCurrentIndex(1))
home.signin_button.clicked.connect(lambda: stack.setCurrentIndex(2))
signup.back_button.clicked.connect(lambda: stack.setCurrentIndex(0))
signin.back_button.clicked.connect(lambda: stack.setCurrentIndex(0))
signin.goto_signup_button.clicked.connect(lambda: stack.setCurrentIndex(1))


def do_logout():
   session.current_user = None
   welcome.greeting.setText("")
   stack.setCurrentIndex(0)


welcome.logout_button.clicked.connect(do_logout)


def open_browse():
    browse.load_categories()
    stack.setCurrentIndex(4)


def open_item(itemID):
    item_detail.load_item(itemID)
    stack.setCurrentIndex(5)


def open_item_manager_manage():
    # Switches to the Item Manager page and selects the Manage tab (index 0)
    item_manager.tabs.setCurrentIndex(0)
    stack.setCurrentIndex(6)


def open_item_manager_queries():
    # Switches to the Item Manager page and selects the Queries tab (index 1)
    item_manager.tabs.setCurrentIndex(1)
    stack.setCurrentIndex(6)


# Wire the Browse logic
browse.on_open_item = open_item
welcome.browse_button.clicked.connect(open_browse)
browse.back_button.clicked.connect(lambda: stack.setCurrentIndex(3))
item_detail.back_button.clicked.connect(open_browse)

# Wire the Item Manager / Queries logic based on welcome.py buttons
welcome.post_item_button.clicked.connect(open_item_manager_manage)
welcome.my_items_button.clicked.connect(open_item_manager_manage)
welcome.queries_button.clicked.connect(open_item_manager_queries)

# Wire the back button from item_manager to return to the Welcome tab
item_manager.back_button.clicked.connect(lambda: stack.setCurrentIndex(3))

# --- Actions ---
signup.create_button.clicked.connect(do_signup)
signin.signin_button.clicked.connect(do_signin)

stack.show()
sys.exit(app.exec())