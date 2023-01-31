import logging
import requests
import json
import configparser
import datetime

from telegram import Update, InputMediaPhoto, InputMediaVideo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from urllib import parse
from custom_ig import customInstagram

###### Config ######
config = configparser.ConfigParser()
config.read('config.ini')
tg_token=config['TG']['token']
log_level=config['Basic']['log_level']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

logger.setLevel(log_level)

def info_log(chat_id, message_id, command, message):
    logger.info("{} - {} - {} - {}".format(chat_id, message_id, command, message))

def error_log(chat_id, message_id, command, message):
    logger.error("{} - {} - {} - {}".format(chat_id, message_id, command, message))

def debug_log(chat_id, message_id, command, message):
    logger.debug("{} - {} - {} - {}".format(chat_id, message_id, command, message))
###### Config ######

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Catch Error to handle
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_log(update.effective_chat.id, update.effective_message.id, 'start/help', 'call')
    botCommands = await context.bot.get_my_commands()
    commands = ''
    for botCommand in botCommands:
        commands = commands + "/{} - {} \n".format(botCommand.command, botCommand.description)
    startText="I'm a Ronnie test bot, use these commands to control me:\n{}".format(commands)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=startText)

async def dtwitter(url: str):
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    ,'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    dtwitter = "https://dtwitter.heismauri.com/"
    FormData = {'url': url, 'selector': "true", 'version': '3.1.0'}
    data = parse.urlencode(FormData)
    content = requests.post(url=dtwitter, headers=HEADERS, data=data).text
    content = json.loads(content, strict=False)
    return content

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

    content = await dtwitter(url)
    mediaList = []

    debug_log(update.effective_chat.id, update.effective_message.id, 'tweet_media', content)

    if hasattr(content, 'error'):
        await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id,text=content["error"])
    else:
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
    
    content = await dtwitter(url)
    mediaList = []
    
    debug_log(update.effective_chat.id, update.effective_message.id, 'tweet_media_lihkg', content)

    if hasattr(content, 'error'):
        await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id,text=content["error"])
    else:
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
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    ,'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    lookupApi = "https://api.tikmate.app/api/lookup"
    FormData = {'url': url}
    data = parse.urlencode(FormData)
    content = requests.post(url=lookupApi, headers=HEADERS, data=data).text
    content = json.loads(content, strict=False)
    downloadUrl = "https://tikmate.app/download/" + content['token'] + "/" + content['id'] + ".mp4?hd=1"
    await context.bot.send_video(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, video=downloadUrl)

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
    
    igPost = await customInstagram.downloadPost(url)
    debug_log(update.effective_chat.id, update.effective_message.id, 'instagram', igPost)
    # Send Video
    if len(igPost['video']) > 0:
        for video in igPost['video']:
            await context.bot.send_video(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, video=video)
    
    # Send Photo(s)
    if len(igPost['image']) > 0:
        mediaList = []
        for image in igPost['image']:
            mediaList.append(InputMediaPhoto(media=image))
        await context.bot.send_media_group(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, media=mediaList)
    info_log(update.effective_chat.id, update.effective_message.id, 'instagram', 'done')

if __name__ == '__main__':
    application = ApplicationBuilder().token(tg_token).build()
    
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', start)
    tweet_media_handler = CommandHandler('tt', tweet_media)
    tweet_media_lihkg_handler = CommandHandler('tl', tweet_media_lihkg)

    tk_video_handler = CommandHandler('tk', tk_video)

    instagram_handler = CommandHandler('ig', instagram)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(tweet_media_handler)
    application.add_handler(tweet_media_lihkg_handler)
    application.add_handler(tk_video_handler)
    application.add_handler(instagram_handler)

    application.add_error_handler(error_handler)
    
    application.run_polling()