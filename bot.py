from telethon import TelegramClient, events
from gtts import gTTS
import random, string, datetime, os
from collections import Counter

api_id = 27557328
api_hash = "7f7e062bcbec01fe3c02c7c898ce3cb7"

client = TelegramClient("kryin_session", api_id, api_hash)

PREFIX = "."

mirror = bold = italic = mono = False
remember = {}
last_seen = {}

VERSION = "2.1 ULTRA"
DEV = "@kryin"

# ===== ГЕН =====
def gen_pass():
    return ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(10))

def gen_nick():
    return random.choice(["dark","ghost","kry","pro"]) + str(random.randint(100,999))

def gen_email():
    return ''.join(random.choices(string.ascii_lowercase,k=8)) + "@gmail.com"


# ===== КОМАНДЫ =====
@client.on(events.NewMessage(outgoing=True))
async def cmd(event):
    global mirror, bold, italic, mono

    text = event.raw_text
    if not text.startswith(PREFIX):
        return

    args = text.split()
    c = args[0][1:]

    # ===== ULTRA HELP =====
    if c == "help":
        return await event.edit(
            f"⚡ **Kryin UserBot** ⚡\n"
            f"╔════════════════════╗\n"
            f"║ 👑 Версия: {VERSION}\n"
            f"║ 👨‍💻 Разраб: {DEV}\n"
            f"╚════════════════════╝\n\n"

            f"📌 **ОСНОВА**\n"
            f"`.ping`  — пинг\n"
            f"`.id`  — id чата\n"
            f"`.readall`  — прочитать всё\n"
            f"`.delme 5`  — удалить свои\n\n"

            f"📊 **АНАЛИТИКА**\n"
            f"`.stat`  — топ активных\n"
            f"`.topday`  — за сегодня\n"
            f"`.messages`  — твои сообщения\n"
            f"`.mentiontop`  — упоминания\n\n"

            f"🎭 **ФАН**\n"
            f"`.meme текст`\n"
            f"`.flip текст`\n"
            f"`.gay`\n\n"

            f"🧠 **ГЕНЕРАТОРЫ**\n"
            f"`.genpass`\n"
            f"`.nickgen`\n"
            f"`.emailgen`\n\n"

            f"🛠 **ИНСТРУМЕНТЫ**\n"
            f"`.quote`\n"
            f"`.seen`\n"
            f"`.remember текст = ответ`\n\n"

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
        return await event.edit("🏓 **Pong!**")

    elif c == "id":
        return await event.edit(f"🆔 **ID:** `{event.chat_id}`")

    elif c == "readall":
        await client.send_read_acknowledge(event.chat_id)
        return await event.edit("👁 **Прочитано**")

    elif c == "delme":
        try:
            n = int(args[1])
            msgs = []
            async for m in client.iter_messages(event.chat_id, from_user='me', limit=n):
                msgs.append(m.id)
            await client.delete_messages(event.chat_id, msgs)
        except:
            await event.edit("❌ `.delme 5`")

    # ===== STAT =====
    elif c == "stat":
        cnt = Counter()
        users = {}

        async for m in client.iter_messages(event.chat_id, limit=300):
            if m.sender_id:
                cnt[m.sender_id]+=1

                if m.sender_id not in users:
                    s = await m.get_sender()
                    users[m.sender_id] = f"@{s.username}" if s.username else s.first_name

        text = "📊 **ТОП АКТИВНЫХ**\n\n"
        medals = ["🥇","🥈","🥉","4️⃣","5️⃣"]

        for i,(uid,count) in enumerate(cnt.most_common(5)):
            name = users.get(uid, str(uid))
            text += f"{medals[i]} {name} — `{count}`\n"

        return await event.edit(text)

    elif c == "topday":
        today=datetime.datetime.now().date()
        cnt=Counter()

        async for m in client.iter_messages(event.chat_id, limit=1000):
            if m.date.date()==today:
                cnt[m.sender_id]+=1

        return await event.edit(f"📊 `{cnt.most_common(5)}`")

    elif c == "messages":
        count=0
        async for _ in client.iter_messages(event.chat_id, from_user='me'):
            count+=1
        return await event.edit(f"📨 `{count}` сообщений")

    elif c == "mentiontop":
        cnt=Counter()

        async for m in client.iter_messages(event.chat_id, limit=500):
            if m.text:
                for w in m.text.split():
                    if w.startswith("@"):
                        cnt[w]+=1

        text = "📊 **ТОП УПОМИНАНИЙ**\n\n"
        for u,cntt in cnt.most_common(5):
            text += f"🔹 {u} — `{cntt}`\n"

        return await event.edit(text)

    # ===== ФАН =====
    elif c == "meme":
        return await event.edit(f"😂 `{text.replace('.meme ','').upper()}`")

    elif c == "flip":
        return await event.edit(f"🙃 `{text.replace('.flip ','')[::-1]}`")

    elif c == "gay":
        return await event.edit(f"🏳️‍🌈 `{random.randint(0,100)}%`")

    # ===== ГЕН =====
    elif c == "genpass":
        return await event.edit(f"🔐 `{gen_pass()}`")

    elif c == "nickgen":
        return await event.edit("\n".join([f"`{gen_nick()}`" for _ in range(5)]))

    elif c == "emailgen":
        return await event.edit("\n".join([f"`{gen_email()}`" for _ in range(5)]))

    # ===== ИНСТРУМЕНТЫ =====
    elif c == "quote":
        if event.is_reply:
            msg=await event.get_reply_message()
            return await event.edit(f"💬 {msg.text}")

    elif c == "seen":
        if not event.is_reply:
            return await event.edit("❌ ответь на сообщение")

        msg = await event.get_reply_message()
        uid = msg.sender_id

        if uid in last_seen:
            delta = datetime.datetime.now() - last_seen[uid]
            return await event.edit(f"👤 `{delta.seconds} сек назад`")
        else:
            return await event.edit("❌ нет данных")

    elif c == "remember":
        try:
            k,v=text.replace(".remember ","").split(" = ")
            remember[k.lower()]=v
            await event.edit("💾 ok")
        except:
            await event.edit("❌ формат")

    # ===== ФОРМАТ =====
    elif c == "mirror":
        mirror=args[1]=="on"
        await event.edit("🔁 ON" if mirror else "🔁 OFF")

    elif c == "bold":
        bold=args[1]=="on"
        await event.edit("🅱️ ON" if bold else "🅱️ OFF")

    elif c == "italic":
        italic=args[1]=="on"
        await event.edit("✍️ ON" if italic else "✍️ OFF")

    elif c == "mono":
        mono=args[1]=="on"
        await event.edit("💻 ON" if mono else "💻 OFF")

    # ===== TTS =====
    elif c == "tts":
        try:
            t=gTTS(text.replace(".tts ",""),lang="ru")
            t.save("v.mp3")
            await client.send_file(event.chat_id,"v.mp3")
            os.remove("v.mp3")
            await event.delete()
        except Exception as e:
            await event.edit(str(e))


# ===== АВТО =====
@client.on(events.NewMessage)
async def auto(event):
    if event.sender_id:
        last_seen[event.sender_id]=datetime.datetime.now()

    if event.out and not event.raw_text.startswith(PREFIX):
        txt=event.raw_text

        if mirror: txt=txt[::-1]
        if bold: txt=f"**{txt}**"
        if italic: txt=f"__{txt}__"
        if mono: txt=f"`{txt}`"

        if txt!=event.raw_text:
            await event.edit(txt)

    if not event.out:
        if event.raw_text.lower() in remember:
            await event.reply(remember[event.raw_text.lower()])


print("🔥 ULTRA USERBOT ЗАПУЩЕН")

client.start()
client.run_until_disconnected()