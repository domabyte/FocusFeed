# Use the official Python 3.10 image
FROM python:3.10-slim

# Set environment variables
ENV POETRY_VERSION=1.1.13
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false

# Install Poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry


# Set the working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install dependencies
RUN poetry install --no-root

# Expose the port the app runs on
EXPOSE 8000

# Set the entry point
CMD ["poetry", "run", "focusfeed"]