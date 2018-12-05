from telethon import TelegramClient, events
from time import sleep
import configparser
import time
import aiocron, asyncio
import logging

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO)

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

api_id = config['API']['id']
api_hash = config['API']['hash']
user_num = config['USER']['number']
user_pass = config['USER']['password']

crons = []

client = TelegramClient('Spameando', api_id, api_hash)
client.start(user_num, user_pass)

@client.on(events.NewMessage(chats='me', pattern='^spam (\w+) mayus (.*$)'))
async def mayus_handler(event):
    user = event.pattern_match.group(1)
    msg = event.pattern_match.group(2).replace(' ', '').upper()
    
    for c in msg:
        print(c)
        await client.send_message(user, c)
    logging.info(f'Spammed mayus to {user}')

@client.on(events.NewMessage(chats='me', pattern='^spam (\w+) colum (\d+) (.*$)'))
async def colum_handler(event):
    user = event.pattern_match.group(1)
    n = int(event.pattern_match.group(2))
    msg = event.pattern_match.group(3).upper()
    formated = '\n'.join([msg[i:i+n] for i in range(0, len(msg), n)])
    await client.send_message(user, formated)
    
    logging.info(f'Spammed colum to {user}')

@client.on(events.NewMessage(chats='me', pattern='^spam (\w+) del (\d+) (.*$)'))
async def del_handler(event):
    user = event.pattern_match.group(1)
    time = int(event.pattern_match.group(2))
    msg = event.pattern_match.group(3)

    send = await client.send_message(user, msg)

    async def del_callback_handler(event):
        logging.info(f'Activated MessageRead callback: {msg}')

        sleep(time)
        await send.delete()
        logging.info(f'Spammed del to {user} after {time}s')
        
        client.remove_event_handler(del_callback_handler)
        logging.info('Removed MessageRead callback')
        
        # Call other callbacks if any
        await client.catch_up()

    client.add_event_handler(del_callback_handler, events.MessageRead(chats=user))
    logging.info('Added MessageRead callback')
    await event.delete()

@client.on(events.NewMessage(chats='me', pattern='^spam (\w+) edit (\d+) (.*) by (.*$)'))
async def edit_handler(event):
    user = event.pattern_match.group(1)
    time = int(event.pattern_match.group(2))
    msg = event.pattern_match.group(3)
    new = event.pattern_match.group(4)

    send = await client.send_message(user, msg)

    async def del_callback_handler(event):
        logging.info(f'Activated MessageRead callback: {msg} -> {new}')

        sleep(time)
        await send.edit(new)
        logging.info(f'Spammed edit to {user} after {time}s')
        
        client.remove_event_handler(del_callback_handler)
        logging.info('Removed MessageRead callback')
        
        # Call other callbacks if any
        await client.catch_up()

    client.add_event_handler(del_callback_handler, events.MessageRead(chats=user))
    logging.info('Added MessageRead callback')
    await event.delete()


@client.on(events.NewMessage(chats='me', pattern='^spam (\w+) repeat (\d+) (.*)'))
async def repeat_handler(event):
    user = event.pattern_match.group(1)
    seg = int(event.pattern_match.group(2))
    msg = event.pattern_match.group(3)

    async def send(): 
        await client.send_message(user, msg)
    
    crons.append(aiocron.crontab(f'* * * * * */{seg}', func=send))
    logging.info(f'Spammed repeat to {user}')

@client.on(events.NewMessage(chats='me', pattern='^spam (\w+) at (\d+):(\d+) (.*)'))
async def at_handler(event):
    user = event.pattern_match.group(1)
    hour = event.pattern_match.group(2)
    minu = event.pattern_match.group(3)
    msg = event.pattern_match.group(4)

    async def send(): 
        await client.send_message(user, msg)
        logging.info(f'Spammed at to {user}')
    
    crons.append(aiocron.crontab(f'{minu} {hour} * * *', func=send))
    logging.info(f'Added cron at {hour}:{minu}')

@client.on(events.NewMessage(chats='me', pattern='^spam stop'))
async def del_handler(event):
    for c in crons:
        c.stop()
    logging.info('Stopped all crons')

logging.info('Start!')
client.run_until_disconnected()
logging.info('Stopped!')

