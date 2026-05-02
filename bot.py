from telethon import TelegramClient, events, functions
from gtts import gTTS
import random, string, os, datetime, asyncio, requests

api_id = 27557328
api_hash = "7f7e062bcbec01fe3c02c7c898ce3cb7"

client = TelegramClient("kryin_session", api_id, api_hash)

PREFIX = "."
VERSION = "16.0 COPY"
DEV = "@kryin"

mirror = bold = italic = mono = False
time_task = None
spam_task = None
copy_user = None

BACKUP_FILE = "profile_backup.txt"
BACKUP_PHOTO = "profile_backup.jpg"

cities = {
    "msk": 3, "spb": 3, "ekb": 5, "nsk": 7,
    "ny": -4, "la": -7,
    "lon": 0, "paris": 1,
    "tokyo": 9
}

def gen_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def mono(t):
    return f"`{t}`"

# ===== COMMANDS =====
@client.on(events.NewMessage(outgoing=True))
async def commands(event):
    global mirror, bold, italic, mono, time_task, spam_task, copy_user

    text = event.raw_text
    if not text.startswith(PREFIX):
        return

    args = text.split()
    cmd = args[0][1:]

    # ===== HELP =====
    if cmd == "help":
        return await event.edit(f"""⚡ Kryin UserBot

Версия: {VERSION}
Разраб: {DEV}

ОСНОВА
` .ping ` ` .id `

ВРЕМЯ
` .time ` ` .timeoff ` ` .timelist `

УТИЛИТЫ
` .calc ` ` .delme `

ГЕНЕРАТОР
` .genpass `

МЕДИА
` .tts `

ПРОФИЛЬ
` .clone ` ` .back `

ФАН
` .roll ` ` .coin ` ` .8ball `

ПОЛЕЗНОЕ
` .weather `

СПАМ
` .spam ` ` .spamstop `

КОПИРОВАНИЕ
` .copy ` ` .copyoff `

ФОРМАТ
` .mirror ` ` .bold ` ` .italic ` ` .mono `
""")

    elif cmd == "ping":
        await event.edit(mono("pong"))

    elif cmd == "id":
        await event.edit(mono(str(event.chat_id)))

    # ===== COPY =====
    elif cmd == "copy":
        if not event.is_reply:
            return await event.edit(mono("ответь на юзера"))

        reply = await event.get_reply_message()
        copy_user = reply.sender_id

        await event.edit(mono("copy ON"))

    elif cmd == "copyoff":
        copy_user = None
        await event.edit(mono("copy OFF"))

    # ===== GENPASS =====
    elif cmd == "genpass":
        await event.edit(mono(gen_password()))

    # ===== ROLL =====
    elif cmd == "roll":
        await event.edit(mono(str(random.randint(1,100))))

    elif cmd == "coin":
        await event.edit(mono(random.choice(["орёл","решка"])))

    elif cmd == "8ball":
        await event.edit(mono(random.choice([
            "да","нет","возможно","позже"
        ])))

    # ===== WEATHER =====
    elif cmd == "weather":
        try:
            data = requests.get(f"https://wttr.in/{args[1]}?format=3").text
            await event.edit(mono(data))
        except:
            await event.edit(mono("error"))

    # ===== SPAM =====
    elif cmd == "spam":
        if args[1].isdigit():
            count = int(args[1])
            msg = " ".join(args[2:])
            await event.delete()
            for _ in range(count):
                await client.send_message(event.chat_id, msg)
                await asyncio.sleep(0.3)
        else:
            msg = " ".join(args[1:])
            await event.delete()

            async def loop():
                while True:
                    await client.send_message(event.chat_id, msg)
                    await asyncio.sleep(0.3)

            spam_task = asyncio.create_task(loop())

    elif cmd == "spamstop":
        if spam_task:
            spam_task.cancel()
            await event.edit(mono("stopped"))

# ===== COPY HANDLER =====
@client.on(events.NewMessage(incoming=True))
async def copier(event):
    global copy_user

    if copy_user and event.sender_id == copy_user:
        try:
            await event.respond(event.text)
        except:
            pass

print("🔥 Kryin UserBot V16 запущен")

client.start()
client.run_until_disconnected()
