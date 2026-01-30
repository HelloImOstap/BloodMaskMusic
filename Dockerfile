FROM python:3.11-slim

RUN apt update && apt install -y \
    ffmpeg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U yt-dlp

CMD ["python", "bot.py"]
