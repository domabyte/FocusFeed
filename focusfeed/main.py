from src.auth import Authenticator
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

    def run(self):
        try:
            while True:
                choice = self.display_menu()
                if choice == "1":
                    self.auth.login()
                elif choice == "2":
                    self.auth.logout()
                elif choice == "3":
                    self.auth.perform_operations()
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
