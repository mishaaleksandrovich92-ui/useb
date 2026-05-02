from telethon import TelegramClient, events
from gtts import gTTS
import random, string, datetime, os, importlib
from collections import Counter

api_id = 27557328
api_hash = "7f7e062bcbec01fe3c02c7c898ce3cb7"

client = TelegramClient("kryin_session", api_id, api_hash)

PREFIX = "."
VERSION = "3.1 ULTRA"
DEV = "@kryin"

mirror = bold = italic = mono = False
msg_cache = {}
PLUGINS = {}

# ===== ПЛАГИНЫ =====
def load_plugins():
    if not os.path.exists("plugins"):
        os.mkdir("plugins")

    for file in os.listdir("plugins"):
        if file.endswith(".py"):
            name = file[:-3]
            try:
                module = importlib.import_module(f"plugins.{name}")
                PLUGINS[name] = module
            except Exception as e:
                print(f"Ошибка плагина {name}: {e}")

load_plugins()

# ===== ГЕНЕРАТОР =====
def gen_pass():
    return ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(10))

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
        return await event.edit(
f"""⚡ Kryin UserBot ⚡

┌───────────────────
👑 Версия: {VERSION}
🤖 Разраб: {DEV}
└───────────────────

📌 ОСНОВА
• `.ping` — пинг
• `.id` — id чата

📊 АНАЛИТИКА
• `.stat` — актив + слова

🧩 ПЛАГИНЫ
• `.plugins` — список
• `.install` — установить
• `.uninstall 1` — удалить

🧠 ГЕНЕРАТОРЫ
• `.genpass` — пароль

🔊 МЕДИА
• `.tts текст` — озвучка

🎨 ФОРМАТ
• `.mirror on/off`
• `.bold on/off`
• `.italic on/off`
• `.mono on/off`

🕵️ ЛОГГЕР
• удаление сообщений
• правка сообщений

⚙️ СИСТЕМА
• работает 24/7 🚀
"""
        )

    # ===== ОСНОВА =====
    elif cmd == "ping":
        await event.edit("🏓 Pong")

    elif cmd == "id":
        await event.edit(f"{event.chat_id}")

    # ===== STAT =====
    elif cmd == "stat":
        users = Counter()
        words = Counter()

        async for m in client.iter_messages(event.chat_id, limit=500):
            if m.sender_id:
                sender = await m.get_sender()
                name = f"@{sender.username}" if sender.username else sender.first_name
                users[name] += 1

            if m.text:
                for w in m.text.lower().split():
                    if len(w) > 3:
                        words[w] += 1

        txt = "📊 Статистика чата\n\n"

        txt += "👥 Топ людей:\n"
        for i,(u,c) in enumerate(users.most_common(5),1):
            txt += f"{i}. {u} — {c}\n"

        txt += "\n💬 Частые слова:\n"
        for w,c in words.most_common(5):
            txt += f"• {w} — {c}\n"

        await event.edit(txt)

    # ===== ПЛАГИНЫ =====
    elif cmd == "plugins":
        if not PLUGINS:
            return await event.edit("❌ нет плагинов")

        txt = "🧩 Плагины:\n\n"
        for i,p in enumerate(PLUGINS,1):
            txt += f"{i}. {p}\n"

        await event.edit(txt)

    elif cmd == "install":
        if not event.is_reply:
            return await event.edit("❌ ответь на файл")

        msg = await event.get_reply_message()
        path = await msg.download_media("plugins/")

        name = os.path.basename(path)[:-3]
        module = importlib.import_module(f"plugins.{name}")
        PLUGINS[name] = module

        await event.edit(f"✅ установлен {name}")

    elif cmd == "uninstall":
        try:
            i = int(args[1]) - 1
            name = list(PLUGINS.keys())[i]
            del PLUGINS[name]
            os.remove(f"plugins/{name}.py")
            await event.edit(f"🗑 удален {name}")
        except:
            await event.edit("❌ ошибка")

    # ===== ФОРМАТ =====
    elif cmd == "mirror":
        mirror = args[1] == "on"
        await event.edit("включено" if mirror else "выключено")

    elif cmd == "bold":
        bold = args[1] == "on"
        await event.edit("включено" if bold else "выключено")

    elif cmd == "italic":
        italic = args[1] == "on"
        await event.edit("включено" if italic else "выключено")

    elif cmd == "mono":
        mono = args[1] == "on"
        await event.edit("включено" if mono else "выключено")

    # ===== TTS =====
    elif cmd == "tts":
        t = gTTS(text.replace(".tts ",""), lang="ru")
        t.save("voice.mp3")
        await client.send_file(event.chat_id, "voice.mp3")
        os.remove("voice.mp3")
        await event.delete()


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

    for i in event.deleted_ids:
        if i in msg_cache:
            await client.send_message(
                event.chat_id,
                f"🗑 Kryin заметил удаление\n📜 {msg_cache[i]}"
            )


@client.on(events.MessageEdited)
async def edit_log(event):
    if not event.is_private:
        return

    old = msg_cache.get(event.id, "нет данных")
    new = event.raw_text

    await event.reply(
        f"✏️ Изменение сообщения\n📜 Было: {old}\n✅ Стало: {new}"
    )

    msg_cache[event.id] = new


# ===== АВТО-ФОРМАТ =====
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


print("🔥 Kryin UserBot запущен")

client.start()
client.run_until_disconnected()
