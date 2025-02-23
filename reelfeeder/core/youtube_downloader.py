import concurrent.futures
import logging
import os
import subprocess
import sys
import time

from dotenv import load_dotenv
from googleapiclient.discovery import build


def setup_logger(logname: str) -> logging.Logger:
    """
    Setup a logger with a file handler.

    Args:
        logname: Path to the log file

    Returns:
        Logger object
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # File handler for logging to a file
    file_handler = logging.FileHandler(logname)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Stream handler for logging to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


class YoutubeDownloader:
    def __init__(
        self, url: str, logname: str, output_path: str, channel_ids: list[str] = None
    ) -> None:
        """
        Initialization of YoutubeDownloader class
        Args:
            url: Youtube video URL
            logname: Path to log file
            output_path: Path for downloaded content
            channel_ids: List of channel IDs to process
        Raises:
            ValueError: If required parameters are invalide
            EnvironmentError: If required environment variables are missing
        """
        if not all([url, logname, output_path]):
            raise ValueError("All parameters must be non-empty")
        self.channel_ids = channel_ids or []
        self.url = url
        self.output_path = output_path
        if not all([os.getenv("GOOGLE_API_KEY")]):
            raise OSError("Missing required environment variables")
        self.logger = setup_logger(logname)
        self.youtube = build("youtube", "v3", developerKey=os.getenv("GOOGLE_API_KEY"))

    @staticmethod
    def __measure_execution_time(func, *args, **kwargs):
        """
        Measures the execution time of a function.

        :param func: The function to measure.
        :param args: Positional arguments to pass to the function.
        :param kwargs: Keyword arguments to pass to the function.
        :return: A tuple containing the result of the function and the time taken in
        seconds.
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        return result, duration

    def __run_yt_dlp_command(self, flag: str, timeout: int = 30) -> tuple[str, str]:
        """
        Execute yt-dlp command with the given flag.
        Args:
            flag: yt-dlp command flag
            timeout: Command execution timeout in seconds

        Returns:
            Tuple of (flag, command output)

        Raises:
            ValueError: If command execution fails
            TimeoutError: If command execution times out
        """
        if not isinstance(self.url, str) or not self.url.startswith(
            ("http://", "https://")
        ):
            raise ValueError(f"Invalid URL: {self.url}")
        command = ["yt-dlp", flag, self.url]
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=timeout, check=True
            )
            return flag, result.stdout.strip()
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out after {timeout} seconds: {command}")
            raise TimeoutError(f"Command timed out: {command}") from None
        except subprocess.CalledProcessError as e:
            self.logger.error(
                f"Command failed with exit code {e.returncode}: {command}"
            )
            self.logger.error(f"Error output: {e.stderr}")
            raise ValueError(f"Command failed: {e.stderr}") from e

    def __get_video_info(self, timeout: int = 60) -> dict:
        """
        Retrieve video information using yt-dlp command concurrently.
        Args:
            timeout: Overall operation timeout in seconds
        Returns:
            Dictionary containing video information
        Raises:
            TimeoutError: If operation times out
        """
        flags = {
            "--get-id": "id",
            "--get-title": "title",
            "--get-duration": "duration",
            "--get-thumbnail": "thumbnail",
            "--get-format": "format",
            "--get-url": "url",
        }
        video_info = {}
        try:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(flags)
            ) as executor:
                future_to_flag = {
                    executor.submit(self.__run_yt_dlp_command, flag): key
                    for flag, key in flags.items()
                }

                for future in concurrent.futures.as_completed(
                    future_to_flag, timeout=timeout
                ):
                    flag = future_to_flag[future]
                    try:
                        flag, result = future.result()
                        if flag in flags:
                            video_info[flags[flag]] = result
                    except Exception as exc:
                        print(f"{flag} generated an exception: {exc}")

            return video_info
        except Exception as exc:
            self.logger.error(f"Failed to get video information: {str(exc)}")

    def get_channel_info(self, channel_id: str) -> dict:
        """
        Retrieve ca channel information using the Youtube API.

        Args:
            channel_id: Youtube channel ID
        Returns:
            Dictionary containing channel information
        Raises:
            ValueError: If channel_id is invalid or channel not found
            RuntimeError: If API request fails
        """
        if not channel_id:
            raise ValueError("channel_id must be non-empty")

        self.logger.info(f"Fetching info for channel : {channel_id}")
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics", id=channel_id
            )
            response = request.execute()

            if "items" in response:
                channel = response["items"][0]
                info = {
                    "title": channel["snippet"]["title"],
                    "description": channel["snippet"]["description"],
                    "subscriber_count": channel["statistics"]["subscriberCount"],
                    "view_count": channel["statistics"]["viewCount"],
                    "video_count": channel["statistics"]["videoCount"],
                    "published_at": channel["snippet"]["publishedAt"],
                }
                self.logger.info(f"Channel Info: {info}")
                return info
            else:
                raise ValueError(f"Channel not found: {channel_id}")
        except Exception as e:
            self.logger.error(f"Failed to get channel info: {str(e)}")
            raise RuntimeError(f"API request failed: {str(e)}") from e

    def channel_info(self) -> tuple[dict, float]:
        """
        Get video and execution time information.
        Returns:
            Tuple of (video information dict, execution time in seconds)
        Raises:
            RuntimeError: If video information cannot be retrieved.
        """
        try:
            video_info, duration = self.__measure_execution_time(self.__get_video_info)
            self.logger.info("Video Info: %s", video_info)
            self.logger.info("Execution Time: %s seconds", duration)
            return video_info, duration
        except Exception as e:
            self.logger.error("Failed to get channel info: %s", str(e))
            raise RuntimeError(f"Failed to get channel info: {str(e)}") from e


def logs_dir():
    """
    Resolve and create logs directory.

    Returns:
        Absolute path to logs directory

    Raises:
        OSError: If directory creation fails
    """
    try:
        # Use a more reliable method to get the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        logs_path = os.path.join(project_root, "logs")

        # Create logs directory if it doesn't exist
        os.makedirs(logs_path, exist_ok=True)

        return logs_path
    except OSError as e:
        raise OSError(f"Failed to create logs directory: {str(e)}") from e


def load_environment() -> None:
    """Load environemnt variables from .env file."""
    if not load_dotenv():
        logging.warning("Failed to load environment variables from .env file")


def main() -> None:
    """
    Main entry point for the Youtube downloader.

    Environment variables required:
    - Channel ID: CHANNEL_ID
    - Google API Key: GOOGLE_API_KEY
    """
    try:
        # Load Environment Variables
        load_environment()
        directory = logs_dir()
        logname = os.path.join(directory, "youtube_downloader.log")

        # Validate environment variables
        if not all([os.getenv("CHANNEL_ID"), os.getenv("GOOGLE_API_KEY")]):
            raise OSError("Missing required environment variables")
        downloader = YoutubeDownloader(
            url=os.getenv("YOUTUBE_URL"),
            logname=logname,
            output_path=os.path.join(directory, "downloads"),
            channel_ids=[os.getenv("CHANNEL_ID")],
        )

        # Get channel information
        video_info, duration = downloader.channel_info()
        downloader.logging.info(
            "Successfully retrieved video information in %.2f seconds", duration
        )
        downloader.logging.info("Video Info: %s", video_info)

    except Exception as e:
        logging.error("Failed to execute main: %s", str(e))
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Application terminated by user ")
        sys.exit(0)
    except Exception as e:
        logging.error("Application Failed: %s", str(e))
        sys.exit(1)
