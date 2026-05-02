from telethon import TelegramClient, events
from gtts import gTTS
import random, string, os
from collections import Counter

api_id = 27557328
api_hash = "7f7e062bcbec01fe3c02c7c898ce3cb7"

client = TelegramClient("kryin_session", api_id, api_hash)

PREFIX = "."
VERSION = "5.0 FINAL"
DEV = "@kryin"

# ===== ПЕРЕКЛЮЧАТЕЛИ =====
mirror = False
bold = False
italic = False
mono = False

msg_cache = {}

# ===== ГЕНЕРАТОРЫ =====
def gen_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def gen_nicks():
    letters = string.ascii_lowercase
    return [f"@{''.join(random.choice(letters) for _ in range(5))}" for _ in range(5)]

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

━━━━━━━━━━━━━━━━━
👑 Версия: {VERSION}
🤖 Разраб: {DEV}
━━━━━━━━━━━━━━━━━

📌 ОСНОВА
• `.ping` — отклик
• `.id` — id чата

📊 АНАЛИТИКА
• `.stat` — топ люди + слова

🧠 ГЕНЕРАТОРЫ
• `.genpass [длина]` — пароль
• `.nickgen` — @ники

🔊 МЕДИА
• `.tts текст` — озвучка

🎨 ФОРМАТ
• `.mirror on/off`
• `.bold on/off`
• `.italic on/off`
• `.mono on/off`

🕵️ ЛОГГЕР (только ЛС)
• отслеживает удаление
• отслеживает правку
""")

    # ===== ОСНОВА =====
    elif cmd == "ping":
        await event.edit("🏓 Pong")

    elif cmd == "id":
        await event.edit(f"🆔 ID: `{event.chat_id}`")

    # ===== GENPASS =====
    elif cmd == "genpass":
        try:
            length = int(args[1]) if len(args) > 1 else 12
        except:
            length = 12

        password = gen_password(length)

        await event.edit(f"""🔐 Пароль

┌───────────────
{password}
└───────────────
""")

    # ===== NICKGEN =====
    elif cmd == "nickgen":
        nicks = gen_nicks()

        txt = "🧠 Никнеймы\n\n"
        for n in nicks:
            txt += f"{n}\n"

        await event.edit(txt)

    # ===== STAT =====
    elif cmd == "stat":
        users = Counter()
        words = Counter()

        async for m in client.iter_messages(event.chat_id, limit=300):
            if m.sender_id:
                sender = await m.get_sender()
                name = f"@{sender.username}" if sender.username else sender.first_name
                users[name] += 1

            if m.text:
                for w in m.text.lower().split():
                    if len(w) > 3:
                        words[w] += 1

        txt = "📊 Статистика\n\n👥 ТОП ЛЮДЕЙ:\n"
        for i, (u, c) in enumerate(users.most_common(5), 1):
            txt += f"{i}. {u} — {c}\n"

        txt += "\n💬 ТОП СЛОВ:\n"
        for w, c in words.most_common(5):
            txt += f"{w} — {c}\n"

        await event.edit(txt)

    # ===== TTS =====
    elif cmd == "tts":
        if len(args) < 2:
            return await event.edit("❌ Напиши текст")

        text_tts = text.replace(".tts ", "")

        tts = gTTS(text_tts, lang="ru")
        tts.save("voice.mp3")

        await client.send_file(event.chat_id, "voice.mp3")
        os.remove("voice.mp3")
        await event.delete()

    # ===== ФОРМАТ =====
    elif cmd == "mirror":
        mirror = args[1] == "on"
        await event.edit(f"🔁 mirror {'ON' if mirror else 'OFF'}")

    elif cmd == "bold":
        bold = args[1] == "on"
        await event.edit(f"🅱 bold {'ON' if bold else 'OFF'}")

    elif cmd == "italic":
        italic = args[1] == "on"
        await event.edit(f"✍ italic {'ON' if italic else 'OFF'}")

    elif cmd == "mono":
        mono = args[1] == "on"
        await event.edit(f"💻 mono {'ON' if mono else 'OFF'}")


# ===== ЛОГГЕР =====
@client.on(events.NewMessage)
async def logger(event):
    if event.is_private and not event.out:
        msg_cache[event.id] = event.raw_text
        if len(msg_cache) > 500:
            msg_cache.pop(next(iter(msg_cache)))

@client.on(events.MessageDeleted)
async def del_log(event):
    if not event.is_private:
        return

    for msg_id in event.deleted_ids:
        if msg_id in msg_cache:
            await client.send_message(
                event.chat_id,
                f"""🗑 Удалено сообщение

📜 Текст:
{msg_cache[msg_id]}"""
            )

@client.on(events.MessageEdited)
async def edit_log(event):
    if not event.is_private:
        return

    old = msg_cache.get(event.id, "нет данных")
    new = event.raw_text

    await event.reply(
        f"""✏️ Сообщение изменено

📜 Было:
{old}

✅ Стало:
{new}"""
    )

    msg_cache[event.id] = new


# ===== АВТО-ФОРМАТ =====
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


print("🔥 Kryin UserBot V5 запущен")

client.start()
client.run_until_disconnected()
