import logging
from telegram import Update, InputMediaPhoto, InputMediaVideo
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
    array = url.split("/")
    L = instaloader.Instaloader()
    L.login("wizone_minju_no1", "minju@angel")
    ##https://www.instagram.com/p/Cgn7fAbviOe/?utm_source=ig_web_copy_link
    post = instaloader.Post.from_shortcode(L.context, array[4])
    mediaList = []
    
    for slide in post.get_sidecar_nodes():
        if slide.is_video:
            mediaList.append(InputMediaVideo(media=slide.video_url))
        else:
            mediaList.append(InputMediaPhoto(media=slide.display_url))
    
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=mediaList)

if __name__ == '__main__':
    application = ApplicationBuilder().token('5447887595:AAGOyswoCpGJYCgRwTkmY0u4hV4n2V-w1Oo').build()
    
    start_handler = CommandHandler('start', start)
    tweet_video_handler = CommandHandler('tweet_video', tweet_video)
    instagram_handler = CommandHandler('instagram', instagram)

    application.add_handler(start_handler)
    application.add_handler(tweet_video_handler)
    application.add_handler(instagram_handler)
    
    application.run_polling()