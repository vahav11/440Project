from PyQt6.QtWidgets import QApplication, QStackedWidget
from pages.home import HomePage
from pages.signup import SignupPage
from pages.signin import SigninPage
from pages.welcome import WelcomePage
import sys
import db

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

stack.addWidget(home)      # 0
stack.addWidget(signup)    # 1
stack.addWidget(signin)    # 2
stack.addWidget(welcome)   # 3


def do_signup():
    if signup.attempt_signup():
        signin.message.setStyleSheet("color: green;")
        signin.message.setText("Account created. Please sign in.")
        stack.setCurrentIndex(2)

def do_signin():
    result = signin.attempt_signin()
    if result:
        firstName, lastName = result
        welcome.greeting.setText(f"Welcome, {firstName} {lastName}")
        stack.setCurrentIndex(3)

# navigation
home.signup_button.clicked.connect(lambda: stack.setCurrentIndex(1))
home.signin_button.clicked.connect(lambda: stack.setCurrentIndex(2))
signup.back_button.clicked.connect(lambda: stack.setCurrentIndex(0))
signin.back_button.clicked.connect(lambda: stack.setCurrentIndex(0))
signin.goto_signup_button.clicked.connect(lambda: stack.setCurrentIndex(1))
def do_logout():
   welcome.greeting.setText("")
   stack.setCurrentIndex(0)


welcome.logout_button.clicked.connect(do_logout) #just in case 

# actions
signup.create_button.clicked.connect(do_signup)
signin.signin_button.clicked.connect(do_signin)

stack.show()
sys.exit(app.exec())