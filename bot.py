import os
import telebot
from PIL import Image
import cv2
import numpy as np
import tempfile
import subprocess

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def upscale_image(image_path, scale=2):
    img = Image.open(image_path)
    new_size = (img.width * scale, img.height * scale)
    img = img.resize(new_size, Image.LANCZOS)
    out_path = image_path.replace(".jpg", "_upscaled.jpg")
    img.save(out_path)
    return out_path

def upscale_video(video_path, scale=2):
    temp_dir = tempfile.mkdtemp()
    upscaled_path = os.path.join(temp_dir, "upscaled.mp4")
    command = [
        "ffmpeg", "-i", video_path,
        "-vf", f"scale=iw*{scale}:ih*{scale}",
        "-c:v", "libx264", "-crf", "18", "-preset", "slow",
        upscaled_path
    ]
    subprocess.run(command)
    return upscaled_path

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    file_data = bot.download_file(file_info.file_path)
    temp_path = "photo.jpg"
    with open(temp_path, "wb") as f:
        f.write(file_data)
    bot.reply_to(message, "🔄 Улучшаю фото...")
    upscaled_path = upscale_image(temp_path, scale=2)
    with open(upscaled_path, "rb") as f:
        bot.send_photo(message.chat.id, f)

@bot.message_handler(content_types=["video"])
def handle_video(message):
    file_info = bot.get_file(message.video.file_id)
    file_data = bot.download_file(file_info.file_path)
    temp_path = "video.mp4"
    with open(temp_path, "wb") as f:
        f.write(file_data)
    bot.reply_to(message, "🔄 Улучшаю видео (это может занять до 1 минуты)...")
    upscaled_path = upscale_video(temp_path, scale=2)
    with open(upscaled_path, "rb") as f:
        bot.send_video(message.chat.id, f)

bot.polling()
