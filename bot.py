from fastapi.responses import FileResponse
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import yt_dlp
from fastapi import FastAPI
import os
import time

app = FastAPI()

async def start(update, context):
    await update.message.reply_text("😛Привіт! Тут ти можеш завантажити музику з YouTube у форматі .mp3\n\n🎤Щоби завантажити музику використовуй цю команду:\n/download URL")

async def download_mp3(update, context):
    if context.args:
        url = context.args[0]
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'python_downloaded_audio/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'
            }]
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl: 
                await update.message.reply_text(f"Завантажую. Очікування займе до 5 хвилин")
                info = ydl.extract_info(url, download=True)
                if "entries" in info:
                    for entry in info["entries"]:
                        file_name = ydl.prepare_filename(entry)
                        mp3_file = os.path.splitext(file_name)[0] + ".mp3"

                        if os.path.exists(mp3_file):
                            with open(mp3_file, "rb") as audio:
                                await update.message.reply_audio(audio)
                            os.remove(mp3_file)
                else:
                    file_name = ydl.prepare_filename(info)
                    mp3_file = os.path.splitext(file_name)[0] + ".mp3"

                    if os.path.exists(mp3_file):
                        with open(mp3_file, "rb") as audio:
                            await update.message.reply_audio(audio)
                        os.remove(mp3_file)
            os.remove(mp3_file)
        except yt_dlp.DownloadError as e:
            await update.message.reply_text(f"❌СИСТЕМНА ПОМИЛКА: {e}")
    else:
        await update.message.reply_text("❌Немає посилання!\n\nБудь ласка, використовуйте дану команду:\n/mp3 URL")

def cleanup_downloads(folder="downloads", max_age_seconds=3600):
    now = time.time()
    if not os.path.exists(folder):
        return

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    print(f"Видалено старий файл: {filename}")
                except Exception as e:
                    print(f"Не вдалося видалити {filename}: {e}")

async def download_mp4(update, context):
    cleanup_downloads()
    if context.args:
        url = context.args[0]
        ydl_opts = {
            "format": "mp4[height<=720]",  # максимум 720p
            "outtmpl": "downloads/%(title)s.%(ext)s"
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await update.message.reply_text("Завантажую відео...")
                info = ydl.extract_info(url, download=True)
                mp4_file = ydl.prepare_filename(info)
                size_mb = os.path.getsize(mp4_file) / (1024 * 1024)
                if size_mb >= 49:
                    filename = os.path.basename(mp4_file)
                    server_url = "https://your-railway-app-url.up.railway.app"
                    file_link = f"{server_url}/downloads/{filename}"
                    await update.message.reply_text(
                        f"⚠️ Файл завеликий для Telegram.\nЗавантажити можна тут:\n{file_link}"
                    )

                with open(mp4_file, "rb") as video:
                    await update.message.reply_video(video)

                os.remove(mp4_file)
        except yt_dlp.DownloadError as e:
            await update.message.reply_text(f"❌СИСТЕМНА ПОМИЛКА: {e}")
    else:
        await update.message.reply_text("❌Немає посилання!\n\nБудь ласка, використовуйте дану команду:\n/mp4 URL")

def main():
    app = Application.builder().token("6372402826:AAEYlHqe06pILxLrJGwtSkaOa4BLoWDkVyk").build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("mp3", download_mp3))
    app.add_handler(CommandHandler("mp4", download_mp4))

    print("Бот запущений...")
    app.run_polling()

if __name__ == "__main__":
    main()

