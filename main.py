from telethon import TelegramClient, events ,sync
from time import sleep
from functools import partial
import configparser
import time
import aiocron, asyncio
import logging
import socks

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO)

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

api_id = config['API']['id']
api_hash = config['API']['hash']
user_num = config['USER']['number']
user_pass = config['USER']['password']

callbacks = []
crons = []

client = TelegramClient('Spameando', api_id, api_hash)
client.start(user_num, user_pass)

log = client.send_message('me', "Spameando init... OK\n\n$")


async def responseLog(event, msg):
    global log
    newlog = f"{log.message} {event.message.message}\n{msg}\n\n$"
    await event.delete()
    log = await log.edit(newlog)


async def send(user, msg):
    await client.send_message(user, msg)
    logging.info(f'Send "{msg}" to {user}')


@client.on(events.NewMessage(chats='me', pattern='^spam status'))
async def status_handler(event):
    await responseLog(event, "I'm here")


@client.on(events.NewMessage(chats='me', pattern='^spam help'))
async def help_handler(event):
    await responseLog(event, "Help is Work In Progress bro :)")


@client.on(events.NewMessage(chats='me', pattern=r'^spam (\w+) mayus (.*$)'))
async def mayus_handler(event):
    user = event.pattern_match.group(1)
    msg = event.pattern_match.group(2).replace(' ', '').upper()
    
    for c in msg:
        print(c)
        await client.send_message(user, c)
    await responseLog(event, f'Spammed mayus to {user}')


@client.on(events.NewMessage(chats='me', pattern=r'^spam (\w+) colum (\d+) (.*$)'))
async def colum_handler(event):
    user = event.pattern_match.group(1)
    n = int(event.pattern_match.group(2))
    msg = event.pattern_match.group(3).upper()
    formated = '\n'.join([msg[i:i+n] for i in range(0, len(msg), n)])
    await client.send_message(user, formated)
    await responseLog(event, f'Spammed colum to {user}')


########### REFACTOR THIS
async def del_callback_handler(time, send, event):
        sleep(time)
        await send.delete()
        client.remove_event_handler(del_callback_handler)
        await client.catch_up()

@client.on(events.NewMessage(chats='me', pattern=r'^spam (\w+) del (\d+) (.*$)'))
async def del_handler(event):
    user = event.pattern_match.group(1)
    time = int(event.pattern_match.group(2))
    msg = event.pattern_match.group(3)

    send = await client.send_message(user, msg)

    c = partial(del_callback_handler, time, send)
    callbacks.append(c)
    client.add_event_handler(c, events.MessageRead(chats=user))
    responseLog(event, 'Added MessageRead callback for del')


########### REFACTOR THIS
async def edit_callback_handler(time, new, send, event):
        sleep(time)
        await send.edit(new)
        client.remove_event_handler(edit_callback_handler)
        await client.catch_up()

@client.on(events.NewMessage(chats='me', pattern=r'^spam (\w+) edit (\d+) (.*) by (.*$)'))
async def edit_handler(event):
    user = event.pattern_match.group(1)
    time = int(event.pattern_match.group(2))
    msg = event.pattern_match.group(3)
    new = event.pattern_match.group(4)

    send = await client.send_message(user, msg)

    c = partial(edit_callback_handler, time, new, send)
    callbacks.append(c)
    client.add_event_handler(c, events.MessageRead(chats=user))
    responseLog(event, 'Added MessageRead callback for edit')


@client.on(events.NewMessage(chats='me', pattern=r'^spam (\w+) repeat (\d+) (.*)'))
async def repeat_handler(event):
    user = event.pattern_match.group(1)
    seg = int(event.pattern_match.group(2))
    msg = event.pattern_match.group(3)

    c = partial(send, user, msg)
    task = aiocron.crontab(f'* * * * * */{seg}', func=c)
    crons.append(task)
    
    responseLog(event, f'Spammed repeat to {user}')


@client.on(events.NewMessage(chats='me', pattern=r'^spam (\w+) at (\d+):(\d+) (.*)'))
async def at_handler(event):
    user = event.pattern_match.group(1)
    hour = event.pattern_match.group(2)
    minu = event.pattern_match.group(3)
    msg = event.pattern_match.group(4)
    
    c = partial(send, user, msg)
    task = aiocron.crontab(f'{minu} {hour} * * *', func=c)
    crons.append(task)
    responseLog(event, f'Added cron at {hour}:{minu} to {user}')


async def say_callback_handler(user, msg, event):
    await client.send_message(user, msg)

@client.on(events.NewMessage(chats='me', pattern=r'^spam (\w+) say (.*$)'))
async def say_handler(event):
    user = event.pattern_match.group(1)
    msg = event.pattern_match.group(2)
    
    c = partial(say_callback_handler, user, msg)
    callbacks.append(c)

    client.add_event_handler(c, events.NewMessage(chats=user))
    await responseLog(event, f'Say "{msg}" always to {user}')


async def mimo_callback_handler(user, event):
    await client.send_message(user, event.message.message)

@client.on(events.NewMessage(chats='me', pattern=r'^spam (\w+) mimo'))
async def mimo_handler(event):
    user = event.pattern_match.group(1)
    c = partial(mimo_callback_handler, user)
    callbacks.append(c)

    client.add_event_handler(c, events.NewMessage(chats=user))
    await responseLog(event, f"Set mimo to {user}")


@client.on(events.NewMessage(chats='me', pattern='^spam stop'))
async def stop_handler(event):
    for c in crons:
        c.stop()
    logging.info('Stopped all crons')

    for c in callbacks:
        client.remove_event_handler(c)
    logging.info('Stopped others events handlers')

    await responseLog(event, "Stopped all")


logging.info('Start!')
client.run_until_disconnected()
logging.info('Stopped!')
