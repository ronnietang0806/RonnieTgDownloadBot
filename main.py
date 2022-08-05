import logging
import requests
import json
import instaloader
import configparser
import datetime

from telegram import Update, InputMediaPhoto, InputMediaVideo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from urllib import parse

###### Config ######
config = configparser.ConfigParser()
config.read('config.ini')
tg_token=config['TG']['token']
ig_username=config['IG']['username']
ig_password=config['IG']['password']
schedule_timer=int(config['DEFAULT']['schedule_timer'])
###### Config ######

###### IG Username #####
ig_username_config = configparser.ConfigParser()
ig_username_config.read('ig_username.ini')
ig_member=ig_username_config['member']
ig_official=ig_username_config['official']
###### IG Username #####

L = instaloader.Instaloader(quiet=True)
L.login(ig_username, ig_password)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def tweet_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{} - {}".format('tweet_photo', update.effective_chat.id))
    if not context.args:
        logging.error("{} - {} - {}".format('tweet_photo', update.effective_chat.id, "Url empty"))
        return
    url = ' '.join(context.args)
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
    dtwitter = "https://dtwitter.heismauri.com/"
    FormData = {'url': url, 'selector': "true", 'version': '3.0.6'}
    data = parse.urlencode(FormData)
    content = requests.post(url=dtwitter, headers=HEADERS, data=data).text
    content = json.loads(content)
    mediaList = []

    for mediaUrl in content["media"]:
        if mediaUrl["type"]=="photo":
            mediaList.append(InputMediaPhoto(media=mediaUrl["link"]))
        else:
             mediaList.append(InputMediaVideo(media=mediaUrl["link"]))
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=mediaList)

async def ig_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{} - {}".format('ig_story', update.effective_chat.id))
    if not context.args:
        logging.error("{} - {} - {}".format('ig_story', update.effective_chat.id, "Username empty"))
        return
    username = ' '.join(context.args)
    profile = instaloader.Profile.from_username(L.context, username)
    videoList = await _get_video_story(update.effective_chat.id, L.get_stories([profile.userid]))
    if (videoList):
        for video in videoList:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video)

    photoList = await _get_photo_story(update.effective_chat.id, L.get_stories([profile.userid]))
    if (photoList):
        if len(photoList) < 5:
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=photoList)
        else:
            while len(photoList) > 0:
                i = 0
                tempList = []
                while i < 5:
                    photo = photoList.pop()
                    tempList.append(photo)
                    i = i + 1
                    if len(photoList) <= 0: break
                await context.bot.send_media_group(chat_id=update.effective_chat.id, media=tempList)

async def _get_video_story(chat_id, stories):
    videoList = []
    for story in stories:
        for item in story.get_items():
            if item.is_video:
                videoList.append(item.video_url)
    return videoList

async def _get_photo_story(chat_id, stories):
    photoList = []
    for story in stories:
        for item in story.get_items():
            if not(item.is_video):
                photoList.append(InputMediaPhoto(media=item.url))
    return photoList

async def ig_story_with_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("{} - {}".format('ig_story_with_keyboard', update.effective_chat.id))
    kb = []
    for key in ig_member:
        kb.append([InlineKeyboardButton(text=key, callback_data=ig_member[key])])
    for key in ig_official:
        kb.append([InlineKeyboardButton(text=key, callback_data=ig_official[key])])
    reply_markup = InlineKeyboardMarkup(kb)
    await update.message.reply_text("Please choose ig:", reply_markup=reply_markup)

async def ig_story_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Selected ig: {query.data}")
    logging.info("{} - {} - {}".format('ig_story_with_keyboard', query.data, update.effective_chat.id))
    profile = instaloader.Profile.from_username(L.context, query.data)
    videoList = await _get_video_story(update.effective_chat.id, L.get_stories([profile.userid]))
    if(videoList):
        for video in videoList:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video)
    
    photoList = await _get_photo_story(update.effective_chat.id, L.get_stories([profile.userid]))
    if(photoList):
        if len(photoList) < 5:
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=photoList)
        else:
            while len(photoList) > 0:
                i = 0
                tempList = []
                while i < 5:
                    photo = photoList.pop()
                    tempList.append(photo)
                    i = i + 1
                    if len(photoList) <= 0: break
                await context.bot.send_media_group(chat_id=update.effective_chat.id, media=tempList)

async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{} - {}".format('instagram', update.effective_chat.id))
    if not context.args:
        logging.error("{} - {} - {}".format('i', update.effective_chat.id, "Url empty"))
        return
    url = ' '.join(context.args)
    array = url.split("/")
    post = instaloader.Post.from_shortcode(L.context, array[4])
    mediaList = await _ig_post_to_list(post)

    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=mediaList)

def _ig_post_polling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{} - {}".format('_ig_post_polling', update.effective_chat.id))
    datetimebefore = datetime.datetime.utcnow() - datetime.timedelta(minutes=schedule_timer)
    for key in ig_member:
        _ig_post_polling_per_user(ig_member[key], update, context, datetimebefore)
    logging.info("{} - {} - {}".format('_ig_post_polling', update.effective_chat.id, 'Done'))

async def _ig_post_polling_per_user(username: str, update: Update, context: ContextTypes.DEFAULT_TYPE, datetimebefore:datetime):
    logging.info("{} - {} - {}".format('_ig_post_polling_per_user', update.effective_chat.id, username))
    profile = instaloader.Profile.from_username(L.context, username)
    posts_sorted_by_date = sorted(profile.get_posts(), key=lambda p: p.date_utc, reverse=True)
    for post in posts_sorted_by_date:
        if post.date_utc > datetimebefore:
            logging.info("{} - {} - {} - {}".format('_ig_post_polling_per_user', update.effective_chat.id, username, post.accessibility_caption))
            mediaList = await _ig_post_to_list(post)
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=mediaList)
        else: break
    logging.info("{} - {} - {} - {}".format('_ig_post_polling_per_user', update.effective_chat.id, username, 'Done'))

async def _ig_post_to_list(post: instaloader.Post):
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
    return mediaList

if __name__ == '__main__':
    application = ApplicationBuilder().token(tg_token).build()
    
    start_handler = CommandHandler('start', start)
    instagram_handler = CommandHandler('i', instagram)
    ig_story_handler = CommandHandler('s', ig_story)
    tweet_media_handler = CommandHandler('t', tweet_media)

    ig_story_with_keyboard_handler = CommandHandler("sc", ig_story_with_keyboard)
    ig_story_callback_handler = CallbackQueryHandler(ig_story_callback)

    start_ig_post_polling_handler = CommandHandler('p', _ig_post_polling)

    application.add_handler(start_handler)
    application.add_handler(instagram_handler)
    application.add_handler(tweet_media_handler)
    application.add_handler(ig_story_handler)
    application.add_handler(ig_story_with_keyboard_handler)
    application.add_handler(ig_story_callback_handler)
    application.add_handler(start_ig_post_polling_handler)
    
    application.run_polling()