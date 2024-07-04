import os
import json
from getpass import getpass
import instaloader


class Authenticator:
    def __init__(
        self, username=None, password=None, session_file="instagram_session.json"
    ):
        self.username = username
        self.password = password
        self.session_file = session_file
        self.loader = instaloader.Instaloader()

    def login(self, force=False):
        """Attempt to log in or use existing session."""
        if not force and self._load_session():
            print("Using saved session...")
            return self.loader

        if not self.username or not self.password:
            self.username = input("Enter your Instagram username: ")
            self.password = getpass("Enter your Instagram password: ")

        try:
            self.loader.login(self.username, self.password)
            self._save_session()
            print("Logged in successfully!")
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            self._two_factor_auth()
        except instaloader.exceptions.BadCredentialsException:
            print("Login failed. Please try again.")
            return self.login(force=True)

        return self.loader

    def _two_factor_auth(self):
        """Handle two-factor authentication."""
        code = input("Enter the two-factor authentication code: ")
        self.loader.two_factor_login(code)
        self._save_session()
        print("Two-factor authentication successful.")

    def _save_session(self):
        """Save the current session to a file."""
        session_data = {
            "username": self.username,
            "session": self.loader.save_session_to_file(self.username),
        }
        with open(self.session_file, "w") as f:
            json.dump(session_data, f)

    def _load_session(self):
        """Load a saved session from a file."""
        if os.path.exists(self.session_file):
            with open(self.session_file, "r") as f:
                session_data = json.load(f)
            self.username = session_data["username"]
            session_file = session_data["session"]
            try:
                self.loader.load_session_from_file(self.username, session_file)
                # Test if the loaded session is valid
                self.loader.test_login()
                return True
            except instaloader.exceptions.LoginRequiredException:
                print("Saved session is invalid. Logging in again.")
        return False

    def logout(self):
        """Log out and remove the saved session."""
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
        print("Logged out successfully.")
