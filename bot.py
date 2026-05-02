from telethon import TelegramClient, events, functions
from gtts import gTTS
import random, string, os, datetime, asyncio

api_id = 27557328
api_hash = "7f7e062bcbec01fe3c02c7c898ce3cb7"

client = TelegramClient("kryin_session", api_id, api_hash)

PREFIX = "."
VERSION = "9.0 FINAL"
DEV = "@kryin"

mirror = bold = italic = mono = False
time_task = None

# ===== BACKUP =====
BACKUP_FILE = "profile_backup.txt"
BACKUP_PHOTO = "profile_backup.jpg"

# ===== ПАПКА ПЛАГИНОВ =====
if not os.path.exists("plugins"):
    os.mkdir("plugins")

# ===== ГОРОДА =====
cities = {
    "msk": 3, "spb": 3,
    "ekb": 5, "nsk": 7,
    "kras": 7, "vlad": 10,

    "kiev": 2, "minsk": 3,

    "ny": -4, "la": -7, "chi": -5,

    "lon": 0, "paris": 1, "berlin": 1,
    "rome": 1, "madrid": 1,

    "dubai": 4, "delhi": 5.5,

    "tokyo": 9, "seoul": 9, "beijing": 8,

    "astana": 6, "almaty": 6
}

# ===== ГЕНЕРАТОР =====
def gen_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# ===== КОМАНДЫ =====
@client.on(events.NewMessage(outgoing=True))
async def commands(event):
    global mirror, bold, italic, mono, time_task

    text = event.raw_text
    if not text.startswith(PREFIX):
        return

    args = text.split()
    cmd = args[0][1:]

    # ===== HELP =====
    if cmd == "help":
        return await event.edit(f"""⚡ Kryin UserBot ⚡

┏━━━━━━━━━━━━━━━━━━━┓
👑 Версия: {VERSION}
🤖 Разраб: {DEV}
┗━━━━━━━━━━━━━━━━━━━┛

📌 ОСНОВА
└ `.ping`
└ `.id`

🌍 ВРЕМЯ
└ `.time город`
└ `.timeoff`
└ `.timelist`

📊 ПРОФИЛЬ
└ `.clone`
└ `.back`

🧠 ГЕНЕРАТОР
└ `.genpass`

🔊 МЕДИА
└ `.tts текст`

📦 ПЛАГИНЫ
└ `.install`
""")

    elif cmd == "ping":
        await event.edit("🏓 Pong")

    elif cmd == "id":
        await event.edit(f"`{event.chat_id}`")

    # ===== TIME =====
    elif cmd == "time":
        if len(args) < 2:
            return await event.edit("пример: .time msk")

        city = args[1].lower()
        if city not in cities:
            return await event.edit("нет такого города")

        offset = cities[city]

        if time_task:
            time_task.cancel()

        async def update_name():
            while True:
                try:
                    now = datetime.datetime.utcnow() + datetime.timedelta(hours=offset)
                    t = now.strftime("[%H:%M]")

                    me = await client.get_me()
                    name = me.first_name.split(" [")[0]

                    await client(functions.account.UpdateProfileRequest(
                        first_name=f"{name} {t}"
                    ))

                    await asyncio.sleep(60)
                except:
                    pass

        time_task = asyncio.create_task(update_name())

        await event.edit(f"🕒 время включено: {city}")

    elif cmd == "timeoff":
        if time_task:
            time_task.cancel()
            time_task = None

        me = await client.get_me()
        name = me.first_name.split(" [")[0]

        await client(functions.account.UpdateProfileRequest(
            first_name=name
        ))

        await event.edit("❌ время выключено")

    elif cmd == "timelist":
        await event.edit("""🌍 Доступные города:

🇷🇺 Россия
msk, spb, ekb, nsk, kras, vlad

🇺🇦🇧🇾
kiev, minsk

🇺🇸 США
ny, la, chi

🇪🇺 Европа
lon, paris, berlin, rome, madrid

🌏 Азия
dubai, delhi, tokyo, seoul, beijing

🇰🇿 Казахстан
astana, almaty
""")

    # ===== GENPASS =====
    elif cmd == "genpass":
        try:
            length = int(args[1]) if len(args) > 1 else 12
        except:
            length = 12

        password = gen_password(length)

        await event.edit(f"""🔐 Пароль

┏━━━━━━━━━━━━━━━┓
`{password}`
┗━━━━━━━━━━━━━━━┛
""")

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

        me = await client.get_me()

        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            f.write(f"{me.first_name}|{me.last_name or ''}")

        try:
            photo = await client.download_profile_photo(me)
            if photo:
                os.rename(photo, BACKUP_PHOTO)
        except:
            pass

        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)

        await client(functions.account.UpdateProfileRequest(
            first_name=user.first_name,
            last_name=user.last_name
        ))

        try:
            photo = await client.download_profile_photo(user)
            if photo:
                file = await client.upload_file(photo)
                await client(functions.photos.UploadProfilePhotoRequest(file=file))
                os.remove(photo)
        except:
            pass

        await event.edit("✅ клонирован (бэкап сохранён)")

    # ===== BACK =====
    elif cmd == "back":
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                data = f.read().split("|")

            await client(functions.account.UpdateProfileRequest(
                first_name=data[0],
                last_name=data[1] if len(data) > 1 else ""
            ))

        if os.path.exists(BACKUP_PHOTO):
            file = await client.upload_file(BACKUP_PHOTO)
            await client(functions.photos.UploadProfilePhotoRequest(file=file))

        await event.edit("♻️ профиль восстановлен")

    # ===== INSTALL =====
    elif cmd == "install":
        if not event.is_reply:
            return await event.edit("ответь на .py")

        msg = await event.get_reply_message()

        if not msg.file or not msg.file.name.endswith(".py"):
            return await event.edit("это не .py")

        path = f"plugins/{msg.file.name}"
        await msg.download_media(path)

        await event.edit(f"📦 установлен: {msg.file.name}")

    # ===== ФОРМАТ =====
    elif cmd == "mirror":
        mirror = args[1] == "on"
        await event.edit(f"mirror {'ON' if mirror else 'OFF'}")

    elif cmd == "bold":
        bold = args[1] == "on"
        await event.edit(f"bold {'ON' if bold else 'OFF'}")

    elif cmd == "italic":
        italic = args[1] == "on"
        await event.edit(f"italic {'ON' if italic else 'OFF'}")

    elif cmd == "mono":
        mono = args[1] == "on"
        await event.edit(f"mono {'ON' if mono else 'OFF'}")


# ===== АВТОФОРМАТ =====
@client.on(events.NewMessage)
async def auto_format(event):
    if event.out and not event.raw_text.startswith(PREFIX):
        txt = event.raw_text

        if mirror:
            txt = txt[::-1]
        if bold:
            txt = f"**{txt}**"
        if italic:
            txt = f"__{txt}__"
        if mono:
            txt = f"`{txt}`"

        if txt != event.raw_text:
            await event.edit(txt)


print("🔥 Kryin UserBot V9 FINAL запущен")

client.start()
client.run_until_disconnected()
