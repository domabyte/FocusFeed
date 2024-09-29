# FocusFeed

FocusFeed is a command-line interface (CLI) bot designed to help you download stories, videos, reels, and more from your favorite Instagram accounts. With a user-friendly interface, you can easily manage your downloads and keep track of your favorite content.

## Features

* **Download Stories:** Easily download full story archives from any public Instagram account.
* **Download Reels:** Capture engaging reels and enjoy them offline.
* **Download Posts:** Grab individual posts or entire profiles effortlessly.
* **User-Friendly Interface:** Simple commands and clear menus make it easy to use.
* **Offline Access:** Enjoy your downloaded content anytime, anywhere, even without an internet connection.

## Installation

To get started with FocusFeed, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FocusFeed.git
   cd FocusFeed
   ```

2. Install Poetry (if not already installed):

   Option A: Using the official installer script:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   Option B: Using pip:
   ```bash
   pip install poetry
   ```

3. Install the project dependencies:
   ```bash
   poetry install
   ```

4. Run the bot:
   ```bash
   poetry run focusfeed
   ```

## Usage

1. Launch the bot by running `poetry run focusfeed`.
2. Follow the on-screen prompts to log in. Enter your Instagram username and password when prompted. FocusFeed securely stores your session for future use, making logins faster.
3. Use the bot's menu to select the type of content you want to download and enter the username of the account you're interested in.

## Development

### Branch Creation

When creating a new branch, follow these guidelines:

- Use descriptive names that reflect the purpose of the branch.
- Use the following format: `feature/description`, `bugfix/description`, or `hotfix/description`.

Example:
```
git checkout -b feature/add-download-options
```

### Commit Formatting

To maintain a clean commit history, adhere to the following commit message format:

```
<type>(<scope>): <subject>

<body>
```

- **type**: The type of change (e.g., feat, fix, docs, style, refactor, test, chore).
- **scope**: The area of the codebase affected (optional).
- **subject**: A brief summary of the change (capitalize the first letter and do not end with a period).
- **body**: A detailed description of the change (optional).

Example:
```
feat(auth): add two-factor authentication support

Implemented two-factor authentication to enhance security during login.
```

### Pipeline Usage

To ensure code quality and streamline the development process, we use a CI/CD pipeline. Follow these steps to set up the pipeline:

1. Ensure that your code passes all tests before pushing changes.
2. Create a pull request for your branch to be reviewed.
3. The pipeline will automatically run tests and checks on the pull request.
4. Once approved, merge the pull request into the main branch.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with a descriptive message.
4. Push your branch and create a pull request.

## Acknowledgments

- [Instaloader](https://instaloader.github.io/) for providing the core functionality to download Instagram content.
- [Poetry](https://python-poetry.org/) for simplifying Python packaging and dependency management.