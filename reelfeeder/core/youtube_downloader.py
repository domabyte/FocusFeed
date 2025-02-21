import concurrent.futures
import logging
import os
import subprocess
import time

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()


class YoutubeDownloader:
    def __init__(self, url, logname, output_path) -> None:
        """
        Initialization of YoutubeDownloader class
        """
        self.channel_ids = ["Oenoclips"]
        self.url = url
        self.output_path = output_path
        self.channel_id = os.getenv("CHANNEL_ID")
        self.logger = logging
        self.logger.basicConfig(
            filename=logname,
            filemode="a",
            format="%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=logging.DEBUG,
        )
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

    def __run_yt_dlp_command(self, flag):
        command = ["yt-dlp", flag, self.url]
        result = subprocess.run(command, capture_output=True, text=True)
        return flag, result.stdout.strip()

    def __get_video_info(self):
        flags = {
            "--get-id": "id",
            "--get-title": "title",
            "--get-duration": "duration",
            "--get-thumbnail": "thumbnail",
            "--get-format": "format",
            "--get-url": "url",
        }
        video_info = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(flags)) as executor:
            future_to_flag = {
                executor.submit(self.__run_yt_dlp_command, flag): key
                for flag, key in flags.items()
            }
            for future in concurrent.futures.as_completed(future_to_flag):
                flag = future_to_flag[future]
                try:
                    flag, result = future.result()
                    if flag in flags:
                        video_info[flags[flag]] = result
                except Exception as exc:
                    print(f"{flag} generated an exception: {exc}")
        return video_info

    def get_channel_info(self, channel_id):
        request = self.youtube.channels().list(part="snippet,statistics", id=channel_id)
        response = request.execute()

        if "items" in response:
            channel = response["items"][0]
            return {
                "title": channel["snippet"]["title"],
                "description": channel["snippet"]["description"],
                "subscriber_count": channel["statistics"]["subscriberCount"],
                "view_count": channel["statistics"]["viewCount"],
                "video_count": channel["statistics"]["videoCount"],
                "published_at": channel["snippet"]["publishedAt"],
            }
        else:
            return None

    def channel_info(self) -> dict:
        """
        Get channel information
        """
        video_info, duration = self.__measure_execution_time(self.__get_video_info)
        self.logger.info("Video Info: %s", video_info)
        print("Execution Time: ", duration)


def logs_dir():
    current_dir = os.getcwd()
    parent = os.path.join(os.path.join(current_dir, os.pardir), os.pardir)
    return os.path.abspath(parent)


def main():
    directory = logs_dir()
    logname = os.path.join(directory, "logs", "youtube_downloader.log")
    downloader = YoutubeDownloader(
        "https://youtube.com/shorts/GT2m7AwLg9o?si=iuViBBk4DXG92BNR", logname, "output"
    )
    downloader.channel_info()


if __name__ == "__main__":
    main()
