import os
from getpass import getpass
from instaloader import (
    Instaloader,
    TwoFactorAuthRequiredException,
    BadCredentialsException,
)

class Authenticator:
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.loader = Instaloader()

    def login(self, force=False):
        """Attempt to log in or use existing session."""
        if not self.username:
            self.username = input("Enter your Instagram username: ")
        if not force and self._load_session():
            print("Using saved session...")
            return self.loader

        if not self.password:
            self.password = getpass("Enter your Instagram password: ")

        try:
            self.loader.login(self.username, self.password)
            self.loader.save_session_to_file()
            print("Logged in successfully!")
        except TwoFactorAuthRequiredException:
            self._two_factor_auth()
        except BadCredentialsException:
            print("Login failed. Please try again.")
            return self.login(force=True)

        return self.loader

    def perform_operations(self):
        """Perform various operations using the loaded session."""
        try:
            test_username = self.loader.test_login()
            print("User name is : ", test_username)

            target_username = input("Enter the username to download stories from: ")
            profile = self.loader.check_profile_id(target_username)
            # Create an absolute path for the download directory
            download_path = os.path.join(os.path.expanduser('~'), 'Documents','FocusFeed', 'media', 'stories')
        
            # Ensure the directory exists
            os.makedirs(download_path, exist_ok=True)

            for story in self.loader.get_stories(userids=[profile.userid]):
                for item in story.get_items():
                    if item.typename == 'GraphStoryVideo':
                        self.loader.download_storyitem(item, target=self.username)
            print(f"Stories of {target_username} downloaded successfully.")
        except Exception as e:
            print(f"Error occurred while performing operations: {e}")
            if "HTTP error code 401" in str(e):
                print("Session might be invalid. Please log in again.")
                self.login(force=True)

    def _two_factor_auth(self):
        """Handle two-factor authentication."""
        code = input("Enter the two-factor authentication code: ")
        self.loader.two_factor_login(code)
        print("Two-factor authentication successful.")

    def _load_session(self):
        """Load a saved session if it exists."""
        if not self.username:
            return False
        try:
            print("User name is : ",self.username)
            self.loader.load_session_from_file(self.username)
            return True
        except FileNotFoundError:
            return False

    def logout(self):
        """Log out and remove the saved session."""
        if self.username:
            session_file = f"{self.username}.session"
            if os.path.exists(session_file):
                os.remove(session_file)
            print("Logged out successfully.")
        else:
            print("No active session to log out from.")
