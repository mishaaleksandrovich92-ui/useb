from telethon import TelegramClient, events
from gtts import gTTS
import random, string, datetime, os, importlib
from collections import Counter

api_id = 27557328
api_hash = "7f7e062bcbec01fe3c02c7c898ce3cb7"

client = TelegramClient("kryin_session", api_id, api_hash)

PREFIX = "."
VERSION = "3.0 PRIVATE"
DEV = "@kryin"

mirror = bold = italic = mono = False
last_seen = {}

# ===== КЭШ ДЛЯ ЛОГГЕРА =====
msg_cache = {}

# ===== ПЛАГИНЫ =====
PLUGINS = {}

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

# ===== ГЕН =====
def gen_pass():
    return ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(10))


# ===== КОМАНДЫ =====
@client.on(events.NewMessage(outgoing=True))
async def cmd(event):
    global mirror, bold, italic, mono

    text = event.raw_text
    if not text.startswith(PREFIX):
        return

    args = text.split()
    c = args[0][1:]

    # ===== HELP =====
    if c == "help":
        return await event.edit(
            f"⚡ **Kryin UserBot**\n"
            f"👑 Версия: {VERSION}\n"
            f"👨‍💻 Разраб: {DEV}\n\n"

            f"📌 **ОСНОВА**\n"
            f"`.ping` — проверить бота\n"
            f"`.id` — id чата\n\n"

            f"📊 **АНАЛИТИКА**\n"
            f"`.stat` — актив + слова\n\n"

            f"🛠 **СИСТЕМА**\n"
            f"`.plugins` — список модулей\n"
            f"`.install` — установить\n"
            f"`.uninstall 1` — удалить\n\n"

            f"🎨 **ФОРМАТ**\n"
            f"`.mirror on/off`\n"
            f"`.bold on/off`\n"
            f"`.italic on/off`\n"
            f"`.mono on/off`\n\n"

            f"🔊 **МЕДИА**\n"
            f"`.tts текст`\n"
        )

    # ===== ОСНОВА =====
    elif c == "ping":
        return await event.edit("🏓 Pong")

    elif c == "id":
        return await event.edit(f"`{event.chat_id}`")

    # ===== STAT =====
    elif c == "stat":
        users = Counter()
        words = Counter()

        async for m in client.iter_messages(event.chat_id, limit=500):
            if m.sender_id:
                sender = await m.get_sender()
                name = f"@{sender.username}" if sender.username else sender.first_name
                users[name]+=1

            if m.text:
                for w in m.text.lower().split():
                    if len(w) > 3:
                        words[w]+=1

        text = "📊 **СТАТИСТИКА ЧАТА**\n\n"

        text += "👥 **ТОП ЛЮДЕЙ:**\n"
        for i,(u,cnt) in enumerate(users.most_common(5),1):
            text += f"{i}. {u} — `{cnt}`\n"

        text += "\n💬 **ЧАСТЫЕ СЛОВА:**\n"
        for w,cnt in words.most_common(5):
            text += f"• `{w}` — {cnt}\n"

        return await event.edit(text)

    # ===== ПЛАГИНЫ =====
    elif c == "plugins":
        if not PLUGINS:
            return await event.edit("❌ нет плагинов")

        txt = "🧩 **ПЛАГИНЫ:**\n\n"
        for i,p in enumerate(PLUGINS,1):
            txt += f"{i}. `{p}`\n"

        return await event.edit(txt)

    elif c == "install":
        if not event.is_reply:
            return await event.edit("❌ ответь на файл")

        msg = await event.get_reply_message()
        path = await msg.download_media("plugins/")

        name = os.path.basename(path)[:-3]
        module = importlib.import_module(f"plugins.{name}")
        PLUGINS[name] = module

        return await event.edit(f"✅ установлен `{name}`")

    elif c == "uninstall":
        try:
            i = int(args[1]) - 1
            name = list(PLUGINS.keys())[i]
            del PLUGINS[name]
            os.remove(f"plugins/{name}.py")
            return await event.edit(f"🗑 удален `{name}`")
        except:
            return await event.edit("❌ ошибка")

    # ===== ФОРМАТ =====
    elif c == "mirror":
        mirror=args[1]=="on"
        await event.edit("ON" if mirror else "OFF")

    elif c == "bold":
        bold=args[1]=="on"
        await event.edit("ON" if bold else "OFF")

    elif c == "italic":
        italic=args[1]=="on"
        await event.edit("ON" if italic else "OFF")

    elif c == "mono":
        mono=args[1]=="on"
        await event.edit("ON" if mono else "OFF")

    # ===== TTS =====
    elif c == "tts":
        t=gTTS(text.replace(".tts ",""),lang="ru")
        t.save("v.mp3")
        await client.send_file(event.chat_id,"v.mp3")
        os.remove("v.mp3")
        await event.delete()


# ===== ЛОГГЕР =====
@client.on(events.NewMessage)
async def logger(event):
    if event.is_private and not event.out:
        msg_cache[event.id] = event.raw_text

        if len(msg_cache) > 500:
            msg_cache.pop(next(iter(msg_cache)))

        if event.sender_id:
            last_seen[event.sender_id]=datetime.datetime.now()


@client.on(events.MessageDeleted)
async def del_log(event):
    if not event.is_private:
        return

    for i in event.deleted_ids:
        if i in msg_cache:
            await client.send_message(
                event.chat_id,
                f"🗑 **Kryin задетектил удаление!**\n"
                f"📜 `{msg_cache[i]}`"
            )


@client.on(events.MessageEdited)
async def edit_log(event):
    if not event.is_private:
        return

    old = msg_cache.get(event.id, "нет данных")
    new = event.raw_text

    await event.reply(
        f"✏️ **Kryin задетектил правку!**\n"
        f"📜 Было: `{old}`\n"
        f"✅ Стало: `{new}`"
    )

    msg_cache[event.id] = new


# ===== АВТО =====
@client.on(events.NewMessage)
async def auto(event):
    if event.out and not event.raw_text.startswith(PREFIX):
        txt=event.raw_text

        if mirror: txt=txt[::-1]
        if bold: txt=f"**{txt}**"
        if italic: txt=f"__{txt}__"
        if mono: txt=f"`{txt}`"

        if txt!=event.raw_text:
            await event.edit(txt)


print("🔥 KRYIN USERBOT V3 PRIVATE")

client.start()
client.run_until_disconnected()
