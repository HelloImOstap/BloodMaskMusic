from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import yt_dlp
import os

async def start(update, context):
    await update.message.reply_text("😛Привіт! Тут ти можеш завантажити музику з YouTube у форматі .mp3\n\n🎤Щоби завантажити музику використовуй цю команду:\n/download URL")

async def download(update, context):
    if context.args:
        url = context.args[0]
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'python_downloaded_audio/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'
            }],
            'cookiefile': "cookie.txt"
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
        await update.message.reply_text("❌Немає посилання!\n\nБудь ласка, використовуйте дану команду:\n/download URL")

def main():
    app = Application.builder().token("6372402826:AAEYlHqe06pILxLrJGwtSkaOa4BLoWDkVyk").build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("download", download))

    print("Бот запущений...")
    app.run_polling()

if __name__ == "__main__":
    main()



