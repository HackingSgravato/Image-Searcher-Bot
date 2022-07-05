import logging
import time

from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from discord_webhook import DiscordWebhook, DiscordEmbed
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
PORT = int(os.environ.get('PORT', 5000))


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '5506167177:AAE-gcdG_NLO1z_8TSCriEKkKZyJNwX61uQ'


limit = 10
folder = None


def start(update, context):
    update.message.reply_text('Hi, digit /help to find out more. Project: https://github.com/HackingSgravato/Image-Searcher-Bot')



def help(update, context):
    update.message.reply_text('/folder [folder directory] to input the images save folder\n/bug [bug explanation] to report a bug and let me fix it\n/search [name] to search the name on google and get the default 10 images\n/setlimit [number] to set the images number limit (default 10)')



def search_for_images(update, context):
    name = " ".join(context.args)
    if len(name) == 0:
        update.message.reply_text('you must had digited the text to search for near /search')
        return

    if folder is None:
        update.message.reply_text('you must had selected a save folder by digiting /folder [folder directory]')
        return

    update.message.reply_text('downloading chrome driver')
    chrome_driver = ChromeDriverManager().install()

    update.message.reply_text('hiding chrome window')
    chrome_options = Options()
    chrome_options.headless = True
    
    update.message.reply_text('initializing driver')
    driver = Chrome(service=Service(chrome_driver), chrome_options=chrome_options)

    update.message.reply_text('getting google')
    driver.get('https://www.google.ca/imghp?hl=en&tab=ri&authuser=0&ogbl')
    driver.find_element(By.ID, 'L2AGLb').click()

    update.message.reply_text(f'searching for {name}')
    search_bar = driver.find_element(By.XPATH, '//*[@id="sbtc"]/div/div[2]/input')
    search_bar.send_keys(name)
    search_bar.send_keys(Keys.ENTER)


    update.message.reply_text('loading images')
    last_height = driver.execute_script('return document.body.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        time.sleep(2)
        new_height = driver.execute_script('return document.body.scrollHeight')
        try:
            driver.find_element(By.XPATH, '//*[@id="islmp"]/div/div/div/div/div[5]/input').click()
            time.sleep(2)
        except:
            pass
        if new_height == last_height:
            break
        last_height = new_height
    update.message.reply_text('images loaded')


    update.message.reply_text('downloading images')
    for i in range(1, limit + 1):
        try:
            driver.find_element(By.XPATH, '//*[@id="islrg"]/div[1]/div['+str(i)+']/a[1]/div[1]/img').screenshot(folder + f'\\image {i}.png')
            update.message.reply_text(f'downloads {i}/{limit}')
        except Exception as e:
            update.message.reply_text(e)
            pass
    update.message.reply_text('done')
    update.message.reply_text(f'images were saved at {folder}')



def save_folder(update, context):
    global folder
    if len(context.args) == 0:
        update.message.reply_text('you must had digited a folder near /folder')
    else:
        folder = " ".join(context.args)
        update.message.reply_text(f'new folder was setted: {folder}')



def change_limit(update, context):
    global limit
    limit = int(" ".join(context.args))
    update.message.reply_text(f'new limit was setted: {limit}')



def bug_report(update, context):
    bug_description = " ".join(context.args)
    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/993808582363578468/xPmYpWySMd1yZ6OErn5sp2cfC4aArHQ4oprGXFFK7f6KnGhHpO_tylu1xZD10yQxRnBj')
    embed = DiscordEmbed(title='User report', description='Bug report', color='03b2f8')
    embed.set_timestamp()
    embed.add_embed_field(name='Infos', value=f'{bug_description}')
    webhook.add_embed(embed)
    response = webhook.execute()
    update.message.reply_text('report submitted')



def echo(update, context):
    update.message.reply_text(update.message.text + '\nUnkwown command, digit /help to find out more.')



def error(update, context):
    logger.warning('Update "%s" ha causato l\'errore "%s"', update, context.error)



def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("bug", bug_report))
    dp.add_handler(CommandHandler("setlimit", change_limit))
    dp.add_handler(CommandHandler("search", search_for_images))
    dp.add_handler(CommandHandler("folder", save_folder))

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://mysterious-atoll-44133.herokuapp.com/' + TOKEN)

    updater.idle()

if __name__ == '__main__':
    main()