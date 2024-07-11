from src.auth import Authenticator
import instaloader
import sys

class InstagramBot:
    def __init__(self):
        self.auth = Authenticator()
        self.loader = None

    def display_menu(self):
        print("\nInstagram Bot")
        print("1. Login")
        print("2. Logout")
        print("3. Perform Operations")
        print("4. Exit")
        return input("Choose an option (1-4): ")

    def login(self):
        if self.loader and self.loader.test_login():
            print("Already logged in!")
        else:
            self.loader = self.auth.login()
            if self.loader and self.loader.test_login():
                print("Logged in successfully!")
            else:
                print("Login failed!")
                self.loader = None

    def logout(self):
        if self.loader:
            self.auth.logout()
            self.loader = None
            print("Logged out successfully!")
        else:
            print("Not logged in!")
            
    def perform_operations(self):
        if not self.loader:
            print("Please login first!")
            return
        print('No operation available at the moment')

    def run(self):
        try:
            while True:
                choice = self.display_menu()
                if choice == "1":
                    self.login()
                elif choice == "2":
                    self.logout()
                elif choice == "3":
                    self.perform_operations()
                elif choice == "4":
                    print("Exiting...")
                    sys.exit(0)
                else:
                    print("Invalid option. Please try again.")
        except KeyboardInterrupt:
            print("\nProgram interrupted. Exiting...")
            sys.exit(0)

def main():
    bot = InstagramBot()
    bot.run()

if __name__ == "__main__":
    main()