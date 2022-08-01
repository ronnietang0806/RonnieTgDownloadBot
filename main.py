import logging
import requests
import json
import instaloader
import configparser
import module

from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from urllib import parse

###### Config ######
config = configparser.ConfigParser()
config.read('config.ini')
tg_token=config['TG']['token']
ig_username=config['IG']['username']
ig_password=config['IG']['password']
###### Config ######

L = instaloader.Instaloader()
L.login(ig_username, ig_password)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def tweet_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{} - {}".format('tweet_video', update.effective_chat.id))
    if not context.args:
        logging.error("{} - {} - {}".format('t', update.effective_chat.id, "Url empty"))
        return
    url = ' '.join(context.args) 
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8', 'Key': '332213fa4a9d4288b5668ddd9'}
    tvdl = "https://tvdl-api.saif.dev"
    FormData = {"url": url, "ver": "1306"}
    data = parse.urlencode(FormData)
    content = requests.post(url=tvdl, headers=HEADERS, data=data).text
    content = json.loads(content)
    videoUrl = content["high"]["downloadURL"]
    await context.bot.send_video(chat_id=update.effective_chat.id, video=videoUrl)

async def tweet_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{} - {}".format('tweet_photo', update.effective_chat.id))
    if not context.args:
        logging.error("{} - {} - {}".format('tweet_photo', update.effective_chat.id, "Url empty"))
        return
    url = ' '.join(context.args)
    #https://twitter.com/IZONEGLOBALTWT/status/1553421572161011713?s=20&t=nk8cMfhFudSxSUWyVVRofQ
    array = url.split("/")
    idArray = array[5].split("?")
    tweet = module.get_tweet(idArray[0])
    logging.info("{} - {} - {}".format('tweet_photo', update.effective_chat.id, tweet))

async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{} - {}".format('instagram', update.effective_chat.id))
    if not context.args:
        logging.error("{} - {} - {}".format('i', update.effective_chat.id, "Url empty"))
        return
    url = ' '.join(context.args)
    array = url.split("/")
    post = instaloader.Post.from_shortcode(L.context, array[4])
    mediaList = []

    if post.mediacount > 1:
        for slide in post.get_sidecar_nodes():
            if slide.is_video:
                mediaList.append(InputMediaVideo(media=slide.video_url))
            else:
                mediaList.append(InputMediaPhoto(media=slide.display_url))
    else:
        if post.is_video:
            mediaList.append(InputMediaVideo(media=post.video_url))
        else:
            mediaList.append(InputMediaPhoto(media=post.url))

    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=mediaList)

if __name__ == '__main__':
    application = ApplicationBuilder().token(tg_token).build()
    
    start_handler = CommandHandler('start', start)
    tweet_video_handler = CommandHandler('t', tweet_video)
    instagram_handler = CommandHandler('i', instagram)
    #tweet_photo_handler = CommandHandler('tweet_photo', tweet_photo)

    application.add_handler(start_handler)
    application.add_handler(tweet_video_handler)
    application.add_handler(instagram_handler)
    #application.add_handler(tweet_photo_handler)
    
    application.run_polling()