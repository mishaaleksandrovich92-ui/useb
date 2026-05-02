from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from gtts import gTTS
import random, string, os, datetime, pytz

api_id = 27557328
api_hash = "7f7e062bcbec01fe3c02c7c898ce3cb7"

client = TelegramClient("kryin_session", api_id, api_hash)

PREFIX = "."
VERSION = "6.0 FIXED"
DEV = "@kryin"

mirror = bold = italic = mono = False

# ===== ПАПКА ПЛАГИНОВ =====
if not os.path.exists("plugins"):
    os.mkdir("plugins")

# ===== ГЕНЕРАТОР =====
def gen_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# ===== TIME =====
cities = {
    "msk": "Europe/Moscow",
    "ekb": "Asia/Yekaterinburg",
    "kiev": "Europe/Kiev",
    "ny": "America/New_York"
}

# ===== КОМАНДЫ =====
@client.on(events.NewMessage(outgoing=True))
async def commands(event):
    global mirror, bold, italic, mono

    text = event.raw_text
    if not text.startswith(PREFIX):
        return

    args = text.split()
    cmd = args[0][1:]

    # ===== HELP =====
    if cmd == "help":
        return await event.edit(f"""
⚡ Kryin UserBot ⚡

Версия: {VERSION}
Разраб: {DEV}

ОСНОВА
• .ping
• .id

СЕРВИСЫ
• .time город
• .timelist

АНАЛИТИКА
• .stat

ГЕНЕРАТОР
• .genpass

МЕДИА
• .tts текст

ПРОФИЛЬ
• .clone (в ответ)

ПЛАГИНЫ
• .install (в ответ на .py)
""")

    elif cmd == "ping":
        await event.edit("pong")

    elif cmd == "id":
        await event.edit(str(event.chat_id))

    # ===== TIME =====
    elif cmd == "time":
        if len(args) < 2:
            return await event.edit("пример: .time msk")

        city = args[1].lower()

        if city not in cities:
            return await event.edit("город не найден")

        tz = pytz.timezone(cities[city])
        now = datetime.datetime.now(tz)

        await event.edit(f"🕒 {city.upper()}: {now.strftime('%H:%M:%S')}")

    elif cmd == "timelist":
        txt = "🌍 Города:\n\n"
        for c in cities:
            txt += f"• {c}\n"
        await event.edit(txt)

    # ===== GENPASS =====
    elif cmd == "genpass":
        password = gen_password()
        await event.edit(f"🔐 {password}")

    # ===== TTS =====
    elif cmd == "tts":
        if len(args) < 2:
            return await event.edit("❌ текст")

        t = gTTS(text.replace(".tts ", ""), lang="ru")
        t.save("voice.mp3")

        await client.send_file(event.chat_id, "voice.mp3")
        os.remove("voice.mp3")
        await event.delete()

    # ===== CLONE =====
    elif cmd == "clone":
        if not event.is_reply:
            return await event.edit("ответь на юзера")

        reply = await event.get_reply_message()
        user = await client(GetFullUserRequest(reply.sender_id))

        await client(functions.account.UpdateProfileRequest(
            first_name=user.user.first_name,
            last_name=user.user.last_name
        ))

        if user.user.photo:
            await client.download_profile_photo(user.user, "avatar.jpg")
            await client.upload_file("avatar.jpg")

        await event.edit("склонировал")

    # ===== INSTALL PLUGIN =====
    elif cmd == "install":
        if not event.is_reply:
            return await event.edit("ответь на .py файл")

        msg = await event.get_reply_message()

        if not msg.file or not msg.file.name.endswith(".py"):
            return await event.edit("это не .py")

        path = f"plugins/{msg.file.name}"
        await msg.download_media(path)

        await event.edit(f"установлен: {msg.file.name}")

    # ===== ФОРМАТ =====
    elif cmd == "mirror":
        mirror = args[1] == "on"
        await event.edit("ok")

    elif cmd == "bold":
        bold = args[1] == "on"
        await event.edit("ok")

    elif cmd == "italic":
        italic = args[1] == "on"
        await event.edit("ok")

    elif cmd == "mono":
        mono = args[1] == "on"
        await event.edit("ok")


# ===== АВТОФОРМАТ =====
@client.on(events.NewMessage)
async def auto(event):
    if event.out and not event.raw_text.startswith(PREFIX):
        txt = event.raw_text

        if mirror: txt = txt[::-1]
        if bold: txt = f"**{txt}**"
        if italic: txt = f"__{txt}__"
        if mono: txt = f"`{txt}`"

        if txt != event.raw_text:
            await event.edit(txt)


print("🔥 Kryin UserBot V6 запущен")

client.start()
client.run_until_disconnected()
