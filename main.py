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
logger = logging.getLogger(__name__)

def info_log(chat_id, message_id, command, message):
    logger.info("{} - {} - {} - {}".format(chat_id, message_id, command, message))

def error_log(chat_id, message_id, command, message):
    logger.error("{} - {} - {} - {}".format(chat_id, message_id, command, message))

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_log(update.effective_chat.id, update.effective_message.id, 'start/help', 'call')
    botCommands = await context.bot.get_my_commands()
    commands = ''
    for botCommand in botCommands:
        commands = commands + "/{} - {} \n".format(botCommand.command, botCommand.description)
    startText="I'm a Ronnie test bot, use these commands to control me:\n{}".format(commands)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=startText)

async def tweet_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_log(update.effective_chat.id, update.effective_message.id, 'tweet_media', 'call')
    if not context.args:
        error_log(update.effective_chat.id, update.effective_message.id, 'tweet_media', "Url empty")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Url empty")
        return
    url = ' '.join(context.args)
    if not url.__contains__('twitter.com'):
        error_log(update.effective_chat.id, update.effective_message.id, 'tweet_media', "Url error")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Url error")
        return
    
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
    dtwitter = "https://dtwitter.heismauri.com/"
    FormData = {'url': url, 'selector': "true", 'version': '3.1.0'}
    data = parse.urlencode(FormData)
    content = requests.post(url=dtwitter, headers=HEADERS, data=data).text
    content = json.loads(content)
    mediaList = []

    if hasattr(content, 'error'):
        await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id,text=content["error"])
        return

    for mediaUrl in content["media"]:
        if mediaUrl["type"]=="photo":
            mediaList.append(InputMediaPhoto(media=mediaUrl["link"]))
        else:
             await context.bot.send_video(chat_id=update.effective_chat.id, video=mediaUrl["link"])
    if mediaList:
        await context.bot.send_media_group(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, media=mediaList)

async def tweet_media_lihkg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_log(update.effective_chat.id, update.effective_message.id, 'tweet_media_lihkg', 'call')
    if not context.args:
        error_log(update.effective_chat.id, update.effective_message.id, 'tweet_media_lihkg', "Url empty")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Url empty")
        return
    url = ' '.join(context.args)
    if not url.__contains__('twitter.com'):
        error_log(update.effective_chat.id, update.effective_message.id, 'tweet_media_lihkg', "Url error")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Url error")
        return
    
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
    dtwitter = "https://dtwitter.heismauri.com/"
    FormData = {'url': url, 'selector': "true", 'version': '3.1.0'}
    data = parse.urlencode(FormData)
    content = requests.post(url=dtwitter, headers=HEADERS, data=data).text
    content = json.loads(content)
    mediaList = []
    
    #if content["error"] is not None:
        #await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id,text=content["error"])
        #return

    for mediaUrl in content["media"]:
        if mediaUrl["type"]=="photo":
            mediaList.append(mediaUrl["link"])
        else:
             info_log(update.effective_chat.id, update.effective_message.id, 'tweet_media_lihkg', 'skip video/gif')
    if mediaList:
        lihkg_content="[url]" + url + "[/url]" 
        for imageLink in mediaList:
            lihkg_content+="[img]"+imageLink+"[/img]"
        await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, text=lihkg_content)

async def ig_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_log(update.effective_chat.id, update.effective_message.id, 'ig_story', 'call')
    if not context.args:
        error_log(update.effective_chat.id, update.effective_message.id, 'ig_story', "Username empty")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Username empty")
        return
    username = ' '.join(context.args)
    info_log(update.effective_chat.id, update.effective_message.id, 'ig_story', username)
    profile = instaloader.Profile.from_username(L.context, username)
    videoList = await _get_video_story(L.get_stories([profile.userid]))
    if (videoList):
        for video in videoList:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video)

    photoList = await _get_photo_story(L.get_stories([profile.userid]))
    if (photoList):
        if len(photoList) < 5:
            await context.bot.send_media_group(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, media=photoList)
        else:
            while len(photoList) > 0:
                i = 0
                tempList = []
                while i < 5:
                    photo = photoList.pop()
                    tempList.append(photo)
                    i = i + 1
                    if len(photoList) <= 0: break
                await context.bot.send_media_group(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, media=tempList)

async def _get_video_story(stories):
    videoList = []
    for story in stories:
        for item in story.get_items():
            if item.is_video:
                videoList.append(item.video_url)
    return videoList

async def _get_photo_story(stories):
    photoList = []
    for story in stories:
        for item in story.get_items():
            if not(item.is_video):
                photoList.append(InputMediaPhoto(media=item.url))
    return photoList

async def ig_story_with_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info_log(update.effective_chat.id, update.effective_message.id, 'ig_story_with_keyboard', 'call')
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
    info_log(update.effective_chat.id, update.effective_message.id, 'ig_story_with_keyboard', query.data)
    profile = instaloader.Profile.from_username(L.context, query.data)
    videoList = await _get_video_story(L.get_stories([profile.userid]))
    if(videoList):
        for video in videoList:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video)
    
    photoList = await _get_photo_story(L.get_stories([profile.userid]))
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
    info_log(update.effective_chat.id, update.effective_message.id, 'instagram', 'call')
    if not context.args:
        error_log(update.effective_chat.id, update.effective_message.id, 'instagram', "Url empty")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Url empty")
        return
    url = ' '.join(context.args)
    
    if not url.__contains__('www.instagram.com'):
        error_log(update.effective_chat.id, update.effective_message.id, 'instagram', "Url error")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Url error")
        return
    
    array = url.split("/")
    post = instaloader.Post.from_shortcode(L.context, array[4])
    tempList = await _ig_post_to_list(post)
    photoList = []
    for media in tempList:
        if type(media) == str:
            await context.bot.send_video(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, video=media)
        else:
            photoList.append(media)
    if photoList:
        await context.bot.send_media_group(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, media=photoList)

async def _ig_post_to_list(post: instaloader.Post):
    mediaList = []
    if post.mediacount > 1:
        for slide in post.get_sidecar_nodes():
            if slide.is_video:
                mediaList.append(slide.video_url)
            else:
                ##info_log('/', '/', '_ig_post_to_list', slide.display_url)
                mediaList.append(InputMediaPhoto(media=slide.display_url))
    else:
        if post.is_video:
            mediaList.append(post.video_url)
        else:
            mediaList.append(InputMediaPhoto(media=post.url))
    return mediaList

async def tk_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_log(update.effective_chat.id, update.effective_message.id, 'tk_video', 'call')
    if not context.args:
        error_log(update.effective_chat.id, update.effective_message.id, 'tk_video', "Url empty")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Url empty")
        return
    url = ' '.join(context.args)
    if not url.__contains__('tiktok'):
        error_log(update.effective_chat.id, update.effective_message.id, 'tk_video', "Url error")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Url error")
        return    
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
    lookupApi = "https://api.tikmate.app/api/lookup"
    FormData = {'url': url}
    data = parse.urlencode(FormData)
    content = requests.post(url=lookupApi, headers=HEADERS, data=data).text
    content = json.loads(content)
    downloadUrl = "https://tikmate.app/download/" + content['token'] + "/" + content['id'] + ".mp4?hd=1"
    await context.bot.send_video(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, video=downloadUrl)

if __name__ == '__main__':
    application = ApplicationBuilder().token(tg_token).build()
    
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', start)
    instagram_handler = CommandHandler('ig', instagram)
    ig_story_handler = CommandHandler('is', ig_story)
    tweet_media_handler = CommandHandler('tt', tweet_media)
    tweet_media_lihkg_handler = CommandHandler('tl', tweet_media_lihkg)

    ig_story_with_keyboard_handler = CommandHandler("sc", ig_story_with_keyboard)
    ig_story_callback_handler = CallbackQueryHandler(ig_story_callback)

    tk_video_handler = CommandHandler('tk', tk_video)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(instagram_handler)
    application.add_handler(tweet_media_handler)
    application.add_handler(tweet_media_lihkg_handler)
    application.add_handler(ig_story_handler)
    application.add_handler(ig_story_with_keyboard_handler)
    application.add_handler(ig_story_callback_handler)
    application.add_handler(tk_video_handler)

    application.add_error_handler(error_handler)
    
    application.run_polling()