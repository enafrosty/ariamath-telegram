import asyncio
import logging
import time
from pathlib import Path

import aiogram
from aiogram import Bot, Dispatcher, types
from spotdl import Song, DownloaderOptions, Spotdl

API_TOKEN = "6893705631:AAGPAhZamv_hfHYprAmq3z68DxyhWB5-NYw"  # Replace with your Telegram bot token
SPOTIFY_CLIENT_ID = "1650881a91af44c0a9551f88dc37d867"  # Replace with your Spotify client ID
SPOTIFY_CLIENT_SECRET = "dda39a45ea5041bbaee237a81ee07260"  # Replace with your Spotify client secret

DOWNLOAD_DIR = "spotify_tracks"
DOWNLOAD_TIMEOUT = 7 * 24 * 60 * 60  # 7 days in seconds

logger = logging.getLogger("root")
logger.setLevel(logging.INFO)

loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN, loop=loop)
dispatcher = Dispatcher(bot=bot)

spotdl = Spotdl(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    downloader_settings=DownloaderOptions(output=DOWNLOAD_DIR),
)


@dispatcher.message_handler(commands=["start"])
async def handle_start_command(message: types.Message):
    if len(message.command) == 2:
        link = message.command[1]

        logger.info(f"Received request for link: {link}")

        try:
            spotify_track = spotdl.search([link])[0]
            _, spotify_track_path = await spotdl.downloader.search_and_download(song=spotify_track)

            await message.reply_audio(audio=types.InputFile(spotify_track_path))
            logger.info(f"Sent Spotify track: {spotify_track.display_name}")
        except Exception as e:
            logger.error(f"Error downloading track: {e}")
            await message.reply("An error occurred while downloading the track.")
    else:
        await message.reply("Please provide a Spotify track link after the /start command.")


async def check_downloaded_tracks():
    logger.info("Started asynchronous function for checking downloaded tracks.")

    while True:
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = Path(DOWNLOAD_DIR) / filename
            file_age = time.time() - os.path.getatime(file_path)

            if file_age > DOWNLOAD_TIMEOUT:
                logger.info(f"Removed track: {filename} (age: {file_age:.2f} hours)")
                os.remove(file_path)

        await asyncio.sleep(60 * 60)  # Check every hour


async def start():
    await dispatcher.start_polling()


if __name__ == "__main__":
    logger.info("Starting asynchronous function for checking downloaded tracks...")
    loop.create_task(check_downloaded_tracks())
    logger.info("Starting Spotify Music Downloader Telegram Bot...")
    loop.run_until_complete(start())
