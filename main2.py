import logging
import requests
import json
import configparser
import datetime

from telegram import Update, InputMediaPhoto, InputMediaVideo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from urllib import parse

###### Config ######
config = configparser.ConfigParser()
config.read('config.ini')
tg_token=config['TG']['token']
ig_username=config['IG']['second_username']
ig_password=config['IG']['second_password']
###### Config ######

###### IG Username #####
ig_username_config = configparser.ConfigParser()
ig_username_config.read('ig_username.ini')
ig_member=ig_username_config['member']
ig_official=ig_username_config['official']
###### IG Username #####

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
    tweet_media_handler = CommandHandler('tt', tweet_media)
    tweet_media_lihkg_handler = CommandHandler('tl', tweet_media_lihkg)

    tk_video_handler = CommandHandler('tk', tk_video)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(tweet_media_handler)
    application.add_handler(tweet_media_lihkg_handler)
    application.add_handler(tk_video_handler)

    application.add_error_handler(error_handler)
    
    application.run_polling()