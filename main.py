# main.py — entry point
from views.login import LoginWindow

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()