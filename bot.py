from telethon import TelegramClient, events, functions
from gtts import gTTS
import random, string, os, datetime

api_id = 27557328
api_hash = "7f7e062bcbec01fe3c02c7c898ce3cb7"

client = TelegramClient("kryin_session", api_id, api_hash)

PREFIX = "."
VERSION = "7.0 ELITE"
DEV = "@kryin"

mirror = bold = italic = mono = False

# ===== ПЛАГИНЫ =====
if not os.path.exists("plugins"):
    os.mkdir("plugins")

# ===== ГЕНЕРАТОР =====
def gen_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# ===== ВРЕМЯ БЕЗ PYTZ =====
cities = {
    "msk": 3,
    "kiev": 2,
    "ny": -4,
    "ekb": 5
}

def get_time(offset):
    utc = datetime.datetime.utcnow()
    return utc + datetime.timedelta(hours=offset)

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
        return await event.edit(f"""⚡ Kryin UserBot ⚡

┏━━━━━━━━━━━━━━━━━━━┓
👑 Версия: {VERSION}
🤖 Разраб: {DEV}
┗━━━━━━━━━━━━━━━━━━━┛

📌 ОСНОВА
└ `.ping` — отклик
└ `.id` — id

🌍 СЕРВИСЫ
└ `.time город` — время
└ `.timelist` — список

📊 АНАЛИТИКА
└ `.stat` — актив

🧠 ГЕНЕРАТОР
└ `.genpass` — пароль

🔊 МЕДИА
└ `.tts текст` — голос

👤 ПРОФИЛЬ
└ `.clone` — копия

📦 ПЛАГИНЫ
└ `.install` — установить .py
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

        now = get_time(cities[city])
        await event.edit(f"🕒 {city.upper()} → {now.strftime('%H:%M:%S')}")

    elif cmd == "timelist":
        txt = "🌍 Доступные города:\n\n"
        for c in cities:
            txt += f"• {c}\n"
        await event.edit(txt)

    # ===== GENPASS =====
    elif cmd == "genpass":
        try:
            length = int(args[1]) if len(args) > 1 else 12
        except:
            length = 12

        await event.edit(f"""🔐 Пароль

┏━━━━━━━━━━━━━━━┓
{gen_password(length)}
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

        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)

        await client(functions.account.UpdateProfileRequest(
            first_name=user.first_name,
            last_name=user.last_name
        ))

        try:
            await client.download_profile_photo(user, "ava.jpg")
            await client(functions.photos.UploadProfilePhotoRequest(
                file=await client.upload_file("ava.jpg")
            ))
        except:
            pass

        await event.edit("✅ клонирован")

    # ===== INSTALL =====
    elif cmd == "install":
        if not event.is_reply:
            return await event.edit("ответь на .py")

        msg = await event.get_reply_message()

        if not msg.file or not msg.file.name.endswith(".py"):
            return await event.edit("это не .py файл")

        path = f"plugins/{msg.file.name}"
        await msg.download_media(path)

        await event.edit(f"📦 установлен: {msg.file.name}\n(перезапусти бота)")

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


print("🔥 Kryin UserBot V7 запущен")

client.start()
client.run_until_disconnected()
