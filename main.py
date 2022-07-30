import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import requests
import json
from urllib import parse
import instaloader

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def tweet_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = ' '.join(context.args)
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8', 'Key': '332213fa4a9d4288b5668ddd9'}
    tvdl = "https://tvdl-api.saif.dev"
    FormData = {"url": url, "ver": "1306"}
    data = parse.urlencode(FormData)
    content = requests.post(url=tvdl, headers=HEADERS, data=data).text
    content = json.loads(content)
    videoUrl = content["high"]["downloadURL"]
    await context.bot.send_video(chat_id=update.effective_chat.id, video=videoUrl)
    logging.info("{} - {}".format('tweet_video', update.effective_chat.id))

async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = ' '.join(context.args)
    L = instaloader.Instaloader()
    L.login()
    posts = instaloader.Profile.from_username(L.context, "instagram").get_posts()

if __name__ == '__main__':
    application = ApplicationBuilder().token('5447887595:AAGOyswoCpGJYCgRwTkmY0u4hV4n2V-w1Oo').build()
    
    start_handler = CommandHandler('start', start)
    tweet_video_handler = CommandHandler('tweet_video', tweet_video)

    application.add_handler(start_handler)
    application.add_handler(tweet_video_handler)
    
    application.run_polling()