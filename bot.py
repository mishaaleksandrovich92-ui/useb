from telethon import TelegramClient, events, functions
from gtts import gTTS
import random, string, os, datetime, asyncio, requests

api_id = 27557328
api_hash = "7f7e062bcbec01fe3c02c7c898ce3cb7"

client = TelegramClient("kryin_session", api_id, api_hash)

PREFIX = "."
VERSION = "14.0 FULL"
DEV = "@kryin"

mirror = bold = italic = mono = False
time_task = None
spam_task = None

BACKUP_FILE = "profile_backup.txt"
BACKUP_PHOTO = "profile_backup.jpg"

cities = {
    "msk": 3, "spb": 3, "ekb": 5, "nsk": 7, "kras": 7, "vlad": 10,
    "kiev": 2, "minsk": 3,
    "ny": -4, "la": -7, "chi": -5,
    "lon": 0, "paris": 1, "berlin": 1, "rome": 1, "madrid": 1,
    "dubai": 4, "delhi": 5.5,
    "tokyo": 9, "seoul": 9, "beijing": 8,
    "astana": 6, "almaty": 6
}

def gen_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@client.on(events.NewMessage(outgoing=True))
async def commands(event):
    global mirror, bold, italic, mono, time_task, spam_task

    text = event.raw_text
    if not text.startswith(PREFIX):
        return

    args = text.split()
    cmd = args[0][1:]

    # ===== HELP =====
    if cmd == "help":
        return await event.edit(f"""⚡ Kryin UserBot ⚡

👑 Версия: {VERSION}
🤖 Разраб: {DEV}

📌 ОСНОВА
• .ping • .id

🌍 ВРЕМЯ
• .time город • .timeoff • .timelist

📊 УТИЛИТЫ
• .calc • .delme

🧠 ГЕНЕРАТОР
• .genpass

🔊 МЕДИА
• .tts

👤 ПРОФИЛЬ
• .clone • .back

🔥 ФАН
• .roll • .coin • .8ball

🌍 ПОЛЕЗНОЕ
• .weather

💣 СПАМ
• .spam • .spamstop

✨ ФОРМАТ
• .mirror • .bold • .italic • .mono
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
            return await event.edit("нет города")

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
        await event.edit(f"🕒 {city}")

    elif cmd == "timeoff":
        if time_task:
            time_task.cancel()
            time_task = None

        me = await client.get_me()
        name = me.first_name.split(" [")[0]

        await client(functions.account.UpdateProfileRequest(first_name=name))
        await event.edit("❌ off")

    elif cmd == "timelist":
        await event.edit(", ".join(cities.keys()))

    # ===== GENPASS =====
    elif cmd == "genpass":
        length = int(args[1]) if len(args) > 1 else 12
        await event.edit(f"🔐\n`{gen_password(length)}`")

    # ===== CALC =====
    elif cmd == "calc":
        try:
            expr = text.replace(".calc ", "")
            result = eval(expr)
            await event.edit(f"🧮 `{expr}` = `{result}`")
        except:
            await event.edit("❌ ошибка")

    # ===== DELME =====
    elif cmd == "delme":
        count = int(args[1])
        deleted = 0

        async for msg in client.iter_messages(event.chat_id, from_user="me"):
            try:
                await msg.delete()
                deleted += 1
                if deleted >= count:
                    break
            except:
                pass

        m = await event.respond(f"🗑 {deleted}")
        await asyncio.sleep(2)
        await m.delete()

    # ===== TTS =====
    elif cmd == "tts":
        t = gTTS(text.replace(".tts ", ""), lang="ru")
        t.save("voice.mp3")
        await client.send_file(event.chat_id, "voice.mp3")
        os.remove("voice.mp3")
        await event.delete()

    # ===== CLONE =====
    elif cmd == "clone":
        if not event.is_reply:
            return await event.edit("ответь")

        me = await client.get_me()

        with open(BACKUP_FILE, "w") as f:
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

        await event.edit("✅ cloned")

    # ===== BACK =====
    elif cmd == "back":
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE) as f:
                data = f.read().split("|")

            await client(functions.account.UpdateProfileRequest(
                first_name=data[0],
                last_name=data[1]
            ))

        if os.path.exists(BACKUP_PHOTO):
            file = await client.upload_file(BACKUP_PHOTO)
            await client(functions.photos.UploadProfilePhotoRequest(file=file))

        await event.edit("♻️ restored")

    # ===== FUN =====
    elif cmd == "roll":
        await event.edit(f"🎲 {random.randint(1,100)}")

    elif cmd == "coin":
        await event.edit(random.choice(["🪙 Орёл", "🪙 Решка"]))

    elif cmd == "8ball":
        await event.edit("🎱 " + random.choice([
            "Да", "Нет", "Скорее да", "Скорее нет",
            "Возможно", "Не думаю", "100%", "Позже"
        ]))

    # ===== WEATHER =====
    elif cmd == "weather":
        city = args[1]
        try:
            data = requests.get(f"https://wttr.in/{city}?format=3").text
            await event.edit(f"🌤 {data}")
        except:
            await event.edit("❌ ошибка")

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
            spam_task = None
            await event.edit("🛑 стоп")

    # ===== FORMAT =====
    elif cmd == "mirror":
        mirror = args[1] == "on"
        await event.edit(f"mirror {mirror}")

    elif cmd == "bold":
        bold = args[1] == "on"
        await event.edit(f"bold {bold}")

    elif cmd == "italic":
        italic = args[1] == "on"
        await event.edit(f"italic {italic}")

    elif cmd == "mono":
        mono = args[1] == "on"
        await event.edit(f"mono {mono}")


@client.on(events.NewMessage(outgoing=True))
async def auto_format(event):
    text = event.raw_text

    if text.startswith(PREFIX):
        return

    new = text

    if mirror:
        new = new[::-1]
    if bold:
        new = f"**{new}**"
    if italic:
        new = f"__{new}__"
    if mono:
        new = f"`{new}`"

    if new != text:
        try:
            await event.edit(new)
        except:
            pass


print("🔥 Kryin UserBot V14 запущен")

client.start()
client.run_until_disconnected()
