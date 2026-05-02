from telethon import TelegramClient, events, functions
from gtts import gTTS
import random, string, os, datetime, asyncio
import importlib.util

api_id = 27557328
api_hash = "7f7e062bcbec01fe3c02c7c898ce3cb7"

client = TelegramClient("kryin_session", api_id, api_hash)

PREFIX = "."
VERSION = "11.0"
DEV = "@kryin"

loaded_plugins = {}   # name -> module
plugin_list = []      # список по номерам

if not os.path.exists("plugins"):
    os.mkdir("plugins")

# ========= LOAD =========
def load_plugin(path):
    name = os.path.basename(path).replace(".py", "")

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)

        if hasattr(module, "register"):
            module.register(client)

        loaded_plugins[name] = module

        if name not in plugin_list:
            plugin_list.append(name)

        return True, name
    except Exception as e:
        return False, str(e)

# ========= RELOAD =========
def reload_plugin(name):
    path = f"plugins/{name}.py"

    if not os.path.exists(path):
        return False, "нет файла"

    try:
        if name in loaded_plugins:
            del loaded_plugins[name]

        return load_plugin(path)
    except Exception as e:
        return False, str(e)

# ========= AUTOSTART =========
for file in os.listdir("plugins"):
    if file.endswith(".py"):
        load_plugin(f"plugins/{file}")

# ========= PASSWORD =========
def gen_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# ========= COMMANDS =========
@client.on(events.NewMessage(outgoing=True))
async def commands(event):
    text = event.raw_text

    if not text.startswith(PREFIX):
        return

    args = text.split()
    cmd = args[0][1:]

    # ===== HELP =====
    if cmd == "help":
        txt = f"""⚡ Kryin UserBot

👑 Версия: {VERSION}
🤖 Разраб: {DEV}

📦 ПЛАГИНЫ
.plugins
.install
.reinstall
.uninstall

🧠 ПРОЧЕЕ
.genpass
.calc
.delme
"""
        return await event.edit(txt)

    # ===== PLUGINS =====
    elif cmd == "plugins":
        if not plugin_list:
            return await event.edit("📦 плагинов нет")

        text = "📦 список плагинов:\n\n"

        for i, name in enumerate(plugin_list, 1):
            text += f"{i}. {name}\n"

        return await event.edit(text)

    # ===== INSTALL =====
    elif cmd == "install":
        if not event.is_reply:
            return await event.edit("ответь на .py")

        msg = await event.get_reply_message()

        if not msg.file or not msg.file.name.endswith(".py"):
            return await event.edit("это не .py")

        path = f"plugins/{msg.file.name}"
        await msg.download_media(path)

        ok, info = load_plugin(path)

        if ok:
            await event.edit(f"✅ установлен: {info}")
        else:
            await event.edit(f"❌ ошибка:\n{info}")

    # ===== REINSTALL =====
    elif cmd == "reinstall":
        if len(args) < 2:
            return await event.edit("номер")

        try:
            num = int(args[1]) - 1
            name = plugin_list[num]
        except:
            return await event.edit("ошибка номера")

        ok, info = reload_plugin(name)

        if ok:
            await event.edit(f"🔄 перезагружен: {name}")
        else:
            await event.edit(f"❌ {info}")

    # ===== UNINSTALL =====
    elif cmd == "uninstall":
        if len(args) < 2:
            return await event.edit("номер")

        try:
            num = int(args[1]) - 1
            name = plugin_list[num]
        except:
            return await event.edit("ошибка")

        path = f"plugins/{name}.py"

        try:
            os.remove(path)
        except:
            pass

        if name in loaded_plugins:
            del loaded_plugins[name]

        plugin_list.remove(name)

        await event.edit(f"🗑 удален: {name}")

    # ===== GENPASS =====
    elif cmd == "genpass":
        length = int(args[1]) if len(args) > 1 else 12
        return await event.edit(f"🔐 `{gen_password(length)}`")

    # ===== CALC =====
    elif cmd == "calc":
        try:
            expr = text.replace(".calc ", "")
            result = eval(expr)
            await event.edit(f"`{expr}` = `{result}`")
        except:
            await event.edit("❌ ошибка")

    # ===== DELME =====
    elif cmd == "delme":
        if len(args) < 2:
            return await event.edit("число")

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

        m = await event.respond(f"🗑 удалено: {deleted}")
        await asyncio.sleep(2)
        await m.delete()


print("🔥 Kryin UserBot V11 запущен")

client.start()
client.run_until_disconnected()
