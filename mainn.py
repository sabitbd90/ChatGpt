# ============================================================
# PREMIUM MULTI AI TELEGRAM BOT
# SINGLE FILE VERSION
# ============================================================

import os
import json
import time
import html
import threading
import requests
import telebot

from concurrent.futures import ThreadPoolExecutor, as_completed
from telebot import types


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = "67645777765567765567776656vffyu77yyy7uyftt66678uhfr5ttfyuyfdr5ygdr5yugftyddyu6yff"

# Fixed Support
SUPPORT_USERNAME = "@tonmoyahmed6891"

# Force Join Channels
FORCE_CHANNELS = [
    {
        "title": "🌐 DARK CYBER 24",
        "username": "@darkcyber24bangladesh",
        "url": "https://t.me/darkcyber24bangladesh"
    },
    {
        "title": "🛡 DCB CYBER SPACE",
        "username": "@dcbcyberspace",
        "url": "https://t.me/dcbcyberspace"
    },
    {
        "title": "⚡ AMCA UPDATE REPOT",
        "username": "@amcaupdaterepot",
        "url": "https://t.me/amcaupdaterepot"
    }
]

# Storage
DATA_FILE = "/sdcard/multi_ai_bot_data.json"

# API
API_TIMEOUT = 12
MAX_WORKERS = 7


# ============================================================
# DEFAULT AI APIs
# ============================================================

DEFAULT_APIS = [
    {
        "name": "Gemini",
        "url": "https://r-bots-free-apis.co08.art/api/gemini",
        "enabled": True,
        "prompt": ""
    },
    {
        "name": "DeepSeek R1",
        "url": "https://r-bots-free-apis.co08.art/api/deepseek-r1",
        "enabled": True,
        "prompt": ""
    },
    {
        "name": "DeepSeek V3",
        "url": "https://r-bots-free-apis.co08.art/api/deepseek-v3",
        "enabled": True,
        "prompt": ""
    },
    {
        "name": "Cohere",
        "url": "https://r-bots-free-apis.co08.art/api/cohere",
        "enabled": True,
        "prompt": ""
    },
    {
        "name": "Qwen",
        "url": "https://r-bots-free-apis.co08.art/api/qwen",
        "enabled": True,
        "prompt": ""
    },
    {
        "name": "Llama Meta",
        "url": "https://r-bots-free-apis.co08.art/api/llama-meta",
        "enabled": True,
        "prompt": ""
    },
    {
        "name": "GPTLogic",
        "url": "https://r-bots-free-apis.co08.art/api/gptlogic",
        "enabled": True,
        "prompt": "be friendly"
    }
]


# ============================================================
# BOT
# ============================================================

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML",
    threaded=True,
    num_threads=12
)


# ============================================================
# LOCKS
# ============================================================

data_lock = threading.RLock()
api_lock = threading.RLock()


# ============================================================
# DATA
# ============================================================

DATA = {
    "users": [],
    "blocked": [],
    "referrals": {},
    "ref_by": {},
    "stats": {
        "messages": 0,
        "success": 0,
        "failed": 0,
        "api_requests": 0
    }
}

APIS = [dict(x) for x in DEFAULT_APIS]


# ============================================================
# STORAGE
# ============================================================

def save_data():
    try:
        with data_lock:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    DATA,
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        return True

    except Exception as e:
        print("[DATA SAVE ERROR]", e)
        return False


def load_data():
    global DATA

    if not os.path.exists(DATA_FILE):
        save_data()
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        if isinstance(loaded, dict):
            DATA.update(loaded)

    except Exception as e:
        print("[DATA LOAD ERROR]", e)


load_data()


# ============================================================
# API STORAGE
# ============================================================

API_FILE = "/sdcard/apis.json"


def save_apis():
    try:
        with api_lock:
            with open(API_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    APIS,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

        return True

    except Exception as e:
        print("[API SAVE ERROR]", e)
        return False


def load_apis():
    global APIS

    if not os.path.exists(API_FILE):
        APIS = [dict(x) for x in DEFAULT_APIS]
        save_apis()
        return

    try:
        with open(API_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        if isinstance(loaded, list):
            APIS = loaded

    except Exception as e:
        print("[API LOAD ERROR]", e)
        APIS = [dict(x) for x in DEFAULT_APIS]
        save_apis()


load_apis()


# ============================================================
# USER HELPERS
# ============================================================

def add_user(user_id):

    changed = False

    with data_lock:

        users = DATA.setdefault("users", [])

        if user_id not in users:
            users.append(user_id)
            changed = True

    if changed:
        save_data()


def is_blocked(user_id):

    with data_lock:
        return user_id in DATA.get("blocked", [])


def total_users():

    with data_lock:
        return len(DATA.get("users", []))


# ============================================================
# REFERRAL
# ============================================================

def get_bot_username():

    try:
        me = bot.get_me()
        return me.username

    except Exception as e:
        print("[BOT USERNAME ERROR]", e)
        return None


BOT_USERNAME = get_bot_username()


def referral_link(user_id):

    if not BOT_USERNAME:
        return ""

    return f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"


def process_referral(user_id, start_parameter):

    if not start_parameter:
        return

    if not start_parameter.startswith("ref_"):
        return

    raw = start_parameter.replace(
        "ref_",
        "",
        1
    ).strip()

    try:
        inviter = int(raw)

    except ValueError:
        return

    # নিজেকে নিজে refer করা যাবে না
    if inviter == user_id:
        return

    with data_lock:

        ref_by = DATA.setdefault(
            "ref_by",
            {}
        )

        referrals = DATA.setdefault(
            "referrals",
            {}
        )

        # একজন user-এর referral একবারই গণনা হবে
        if str(user_id) in ref_by:
            return

        ref_by[str(user_id)] = inviter

        inviter_key = str(inviter)

        referrals[inviter_key] = (
            referrals.get(
                inviter_key,
                0
            ) + 1
        )

    save_data()

    try:
        bot.send_message(
            inviter,
            f"""
🎉 <b>NEW REFERRAL!</b>

একজন নতুন user আপনার
referral link দিয়ে bot-এ এসেছে।

👤 User ID:
<code>{user_id}</code>

🎁 আপনার মোট referral:
<b>{DATA["referrals"].get(str(inviter), 0)}</b>
"""
        )

    except Exception:
        pass


def referral_count(user_id):

    with data_lock:
        return DATA.get(
            "referrals",
            {}
        ).get(
            str(user_id),
            0
        )


# ============================================================
# FORCE JOIN CHECK
# ============================================================

def is_member(user_id, channel_username):

    try:

        member = bot.get_chat_member(
            channel_username,
            user_id
        )

        status = member.status

        if status in [
            "member",
            "administrator",
            "creator"
        ]:
            return True

        return False

    except Exception as e:

        print(
            "[JOIN CHECK ERROR]",
            channel_username,
            e
        )

        return False


def check_force_join(user_id):

    missing = []

    for channel in FORCE_CHANNELS:

        if not is_member(
            user_id,
            channel["username"]
        ):
            missing.append(channel)

    return missing


# ============================================================
# FORCE JOIN UI
# ============================================================

def force_join_keyboard(missing=None):

    if missing is None:
        missing = FORCE_CHANNELS

    keyboard = types.InlineKeyboardMarkup(
        row_width=1
    )

    for channel in missing:

        keyboard.add(
            types.InlineKeyboardButton(
                channel["title"],
                url=channel["url"]
            )
        )

    keyboard.add(
        types.InlineKeyboardButton(
            "✅ আমি সব চ্যানেলে Join করেছি",
            callback_data="verify_join"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🆘 Support",
            url="https://t.me/tonmoyahmed6891"
        )
    )

    return keyboard


def force_join_message(missing=None):

    count = len(
        missing if missing is not None
        else FORCE_CHANNELS
    )

    return f"""
<b>🔐 ACCESS VERIFICATION</b>

━━━━━━━━━━━━━━━━━━

বট ব্যবহার করার আগে আমাদের
<b>{count}টি Channel</b> Join করতে হবে।

নিচের Channel গুলোতে Join করুন
তারপর নিচের

<b>✅ আমি সব চ্যানেলে Join করেছি</b>

বাটনে চাপ দিন।

━━━━━━━━━━━━━━━━━━

🔒 <b>Secure Access</b>
⚡ <b>Fast Verification</b>
🤖 <b>AI Assistant</b>
"""


# ============================================================
# PREMIUM MAIN MENU
# ============================================================

def main_menu():

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        "🤖 AI CHAT",
        "👤 PROFILE"
    )

    keyboard.row(
        "🔗 REFER & EARN",
        "📊 MY STATS"
    )

    keyboard.row(
        "ℹ️ ABOUT",
        "🆘 SUPPORT"
    )

    return keyboard


# ============================================================
# PROFILE PHOTO
# ============================================================

def get_profile_photo(user_id):

    try:

        photos = bot.get_user_profile_photos(
            user_id,
            limit=1
        )

        if not photos or photos.total_count == 0:
            return None

        photo = photos.photos[0][-1]

        file_info = bot.get_file(
            photo.file_id
        )

        downloaded = bot.download_file(
            file_info.file_path
        )

        filename = (
            f"/sdcard/"
            f"ai_bot_profile_{user_id}.jpg"
        )

        with open(
            filename,
            "wb"
        ) as f:
            f.write(downloaded)

        return filename

    except Exception as e:

        print(
            "[PROFILE PHOTO ERROR]",
            e
        )

        return None


# ============================================================
# START WELCOME
# ============================================================

@bot.message_handler(commands=["start"])
def start(message):

    user = message.from_user
    user_id = user.id

    add_user(user_id)

    # Referral
    parts = message.text.split(
        maxsplit=1
    )

    parameter = (
        parts[1]
        if len(parts) > 1
        else ""
    )

    process_referral(
        user_id,
        parameter
    )

    # Force Join
    missing = check_force_join(
        user_id
    )

    if missing:

        name = html.escape(
            user.first_name or "Friend"
        )

        text = f"""
<b>👋 WELCOME, {name}</b>

━━━━━━━━━━━━━━━━━━

🤖 <b>PREMIUM MULTI AI</b>

একাধিক AI ব্যবহার করে
দ্রুত ও স্মার্ট উত্তর পাওয়ার
জন্য এই Bot তৈরি করা হয়েছে।

কিন্তু প্রথমে নিচের Channel
গুলোতে Join করতে হবে।

━━━━━━━━━━━━━━━━━━

🔐 <b>Join Required</b>

তারপর নিচের Verify Button
চাপ দিন।
"""

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=force_join_keyboard(
                missing
            )
        )

        return

    send_welcome(
        message
    )


def send_welcome(message):

    user = message.from_user
    user_id = user.id

    name = html.escape(
        user.first_name or "Friend"
    )

    text = f"""
<b>🤖 PREMIUM AI ASSISTANT</b>

━━━━━━━━━━━━━━━━━━

👋 স্বাগতম <b>{name}</b>

আপনি এখন আমাদের
Premium AI Assistant ব্যবহার
করতে পারবেন।

⚡ <b>7 AI Engines</b>
🚀 <b>Parallel Processing</b>
🏆 <b>First Valid Response</b>
🔄 <b>Automatic Fallback</b>
🛡 <b>Smart Error Handling</b>

━━━━━━━━━━━━━━━━━━

নিচের <b>🤖 AI CHAT</b> বাটনে
চাপ দিয়ে প্রশ্ন করুন।

━━━━━━━━━━━━━━━━━━

🔗 Referral:
<b>{referral_count(user_id)}</b> জন
"""

    photo = get_profile_photo(
        user_id
    )

    try:

        if photo and os.path.exists(photo):

            with open(
                photo,
                "rb"
            ) as f:

                bot.send_photo(
                    message.chat.id,
                    f,
                    caption=text,
                    reply_markup=main_menu()
                )

            try:
                os.remove(photo)
            except Exception:
                pass

        else:

            bot.send_message(
                message.chat.id,
                text,
                reply_markup=main_menu()
            )

    except Exception as e:

        print(
            "[WELCOME ERROR]",
            e
        )

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=main_menu()
        )


# ============================================================
# VERIFY JOIN
# ============================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data == "verify_join"
)
def verify_join(call):

    user_id = call.from_user.id

    missing = check_force_join(
        user_id
    )

    if missing:

        bot.answer_callback_query(
            call.id,
            "❌ সব Channel Join করা হয়নি।",
            show_alert=True
        )

        try:

            bot.edit_message_text(
                force_join_message(
                    missing
                ),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=force_join_keyboard(
                    missing
                )
            )

        except Exception:
            pass

        return

    bot.answer_callback_query(
        call.id,
        "✅ Verification Successful!"
    )

    try:
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
    except Exception:
        pass

    send_welcome(
        call.message
    )


# ============================================================
# HELP
# ============================================================

@bot.message_handler(commands=["help"])
def help_command(message):

    missing = check_force_join(
        message.from_user.id
    )

    if missing:
        bot.send_message(
            message.chat.id,
            force_join_message(
                missing
            ),
            reply_markup=force_join_keyboard(
                missing
            )
        )
        return

    bot.send_message(
        message.chat.id,
        """
<b>📚 HELP CENTER</b>

━━━━━━━━━━━━━━━━━━

🤖 <b>AI CHAT</b>
প্রশ্ন লিখে পাঠান।

🔗 <b>REFER</b>
নিজের referral link শেয়ার করুন।

👤 <b>PROFILE</b>
নিজের Telegram তথ্য দেখুন।

📊 <b>MY STATS</b>
নিজের referral statistics দেখুন।

🆘 <b>SUPPORT</b>
Support-এর সাথে যোগাযোগ করুন।

━━━━━━━━━━━━━━━━━━

/cancel — Main Menu
""",
        reply_markup=main_menu()
    )


# ============================================================
# CANCEL
# ============================================================

@bot.message_handler(commands=["cancel"])
def cancel(message):

    missing = check_force_join(
        message.from_user.id
    )

    if missing:

        bot.send_message(
            message.chat.id,
            force_join_message(
                missing
            ),
            reply_markup=force_join_keyboard(
                missing
            )
        )

        return

    bot.send_message(
        message.chat.id,
        "🏠 <b>Main Menu</b>",
        reply_markup=main_menu()
    )


# ============================================================
# AI CHAT BUTTON
# ============================================================

@bot.message_handler(
    func=lambda m:
    m.text == "🤖 AI CHAT"
)
def ai_chat(message):

    missing = check_force_join(
        message.from_user.id
    )

    if missing:

        bot.send_message(
            message.chat.id,
            force_join_message(
                missing
            ),
            reply_markup=force_join_keyboard(
                missing
            )
        )

        return

    bot.send_message(
        message.chat.id,
        """
<b>🤖 AI CHAT MODE</b>

━━━━━━━━━━━━━━━━━━

আপনার প্রশ্ন এখন পাঠান।

উদাহরণ:

<code>বাংলাদেশের রাজধানী কী?</code>

<code>Python কী?</code>

<code>একটি সুন্দর Facebook caption লিখে দাও</code>

━━━━━━━━━━━━━━━━━━

❌ Main Menu-তে যেতে:
/cancel
""",
        reply_markup=types.ReplyKeyboardRemove()
    )


# ============================================================
# PROFILE
# ============================================================

@bot.message_handler(
    func=lambda m:
    m.text == "👤 PROFILE"
)
def profile(message):

    missing = check_force_join(
        message.from_user.id
    )

    if missing:

        bot.send_message(
            message.chat.id,
            force_join_message(
                missing
            ),
            reply_markup=force_join_keyboard(
                missing
            )
        )

        return

    user = message.from_user

    name = html.escape(
        user.first_name or "Not Set"
    )

    username = (
        "@" + user.username
        if user.username
        else "Not Set"
    )

    count = referral_count(
        user.id
    )

    text = f"""
<b>👤 MY PROFILE</b>

━━━━━━━━━━━━━━━━━━

👤 Name:
<b>{name}</b>

🔗 Username:
<b>{html.escape(username)}</b>

🆔 Telegram ID:
<code>{user.id}</code>

🎁 My Referrals:
<b>{count}</b>

━━━━━━━━━━━━━━━━━━

🤖 Premium AI User
"""

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu()
    )


# ============================================================
# REFERRAL BUTTON
# ============================================================

@bot.message_handler(
    func=lambda m:
    m.text == "🔗 REFER & EARN"
)
def refer_button(message):

    missing = check_force_join(
        message.from_user.id
    )

    if missing:

        bot.send_message(
            message.chat.id,
            force_join_message(
                missing
            ),
            reply_markup=force_join_keyboard(
                missing
            )
        )

        return

    link = referral_link(
        message.from_user.id
    )

    count = referral_count(
        message.from_user.id
    )

    keyboard = types.InlineKeyboardMarkup()

    share_url = (
        "https://t.me/share/url"
        "?url="
        + link
        + "&text="
        + "🤖 Premium AI Assistant ব্যবহার করুন!"
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📤 SHARE REFERRAL LINK",
            url=share_url
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📊 MY REFERRALS",
            callback_data="my_referrals"
        )
    )

    bot.send_message(
        message.chat.id,
        f"""
<b>🔗 REFER & EARN</b>

━━━━━━━━━━━━━━━━━━

আপনার Personal Referral Link:

<code>{link}</code>

━━━━━━━━━━━━━━━━━━

👥 Total Referrals:
<b>{count}</b>

বন্ধুদের এই Link পাঠান।

তারা Link দিয়ে Bot-এ
Join করলে Referral হিসেবে
গণনা হবে।

━━━━━━━━━━━━━━━━━━

📤 নিচের Button চাপ দিয়ে
সরাসরি Share করতে পারবেন।
""",
        reply_markup=keyboard
    )


# ============================================================
# REFERRAL CALLBACK
# ============================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data == "my_referrals"
)
def my_referrals(call):

    count = referral_count(
        call.from_user.id
    )

    bot.answer_callback_query(
        call.id
    )

    try:
        bot.send_message(
            call.message.chat.id,
            f"""
<b>📊 REFERRAL STATISTICS</b>

━━━━━━━━━━━━━━━━━━

👥 Successful Referrals:
<b>{count}</b>

🔗 Your Link:

<code>{referral_link(call.from_user.id)}</code>
"""
        )

    except Exception:
        pass


# ============================================================
# MY STATS
# ============================================================

@bot.message_handler(
    func=lambda m:
    m.text == "📊 MY STATS"
)
def my_stats(message):

    missing = check_force_join(
        message.from_user.id
    )

    if missing:

        bot.send_message(
            message.chat.id,
            force_join_message(
                missing
            ),
            reply_markup=force_join_keyboard(
                missing
            )
        )

        return

    count = referral_count(
        message.from_user.id
    )

    with data_lock:

        total = len(
            DATA.get(
                "users",
                []
            )
        )

    bot.send_message(
        message.chat.id,
        f"""
<b>📊 MY STATISTICS</b>

━━━━━━━━━━━━━━━━━━

🎁 Your Referrals:
<b>{count}</b>

👥 Bot Users:
<b>{total}</b>

🟢 Bot Status:
<b>ONLINE</b>

━━━━━━━━━━━━━━━━━━

Keep sharing your referral link!
""",
        reply_markup=main_menu()
    )


# ============================================================
# ABOUT
# ============================================================

@bot.message_handler(
    func=lambda m:
    m.text == "ℹ️ ABOUT"
)
def about(message):

    missing = check_force_join(
        message.from_user.id
    )

    if missing:

        bot.send_message(
            message.chat.id,
            force_join_message(
                missing
            ),
            reply_markup=force_join_keyboard(
                missing
            )
        )

        return

    bot.send_message(
        message.chat.id,
        """
<b>ℹ️ ABOUT PREMIUM AI</b>

━━━━━━━━━━━━━━━━━━

🤖 Multi AI Assistant

এই Bot একই সময়ে একাধিক
AI API-তে Request পাঠায়।

যে API প্রথমে Valid Response
দেয় সেটি User-এর কাছে পাঠানো হয়।

⚡ Fast Response
🚀 Parallel Processing
🔄 Auto Fallback
🛡 Error Handling
📡 Multiple AI Engines

━━━━━━━━━━━━━━━━━━

Developed for Premium AI
Experience.
""",
        reply_markup=main_menu()
    )


# ============================================================
# SUPPORT
# ============================================================

@bot.message_handler(
    func=lambda m:
    m.text == "🆘 SUPPORT"
)
def support(message):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "🆘 CONTACT SUPPORT",
            url="https://t.me/tonmoyahmed6891"
        )
    )

    bot.send_message(
        message.chat.id,
        f"""
<b>🆘 SUPPORT CENTER</b>

━━━━━━━━━━━━━━━━━━

কোনো সমস্যা হলে আমাদের
Support-এর সাথে যোগাযোগ করুন।

👤 Support:
<b>{SUPPORT_USERNAME}</b>

━━━━━━━━━━━━━━━━━━

নিচের Button ব্যবহার করুন।
""",
        reply_markup=keyboard
    )


# ============================================================
# SPECIAL COMMAND
# /2 @username
# ============================================================

@bot.message_handler(
    func=lambda m:
    m.text.strip().startswith("/2")
)
def support_id_command(message):

    missing = check_force_join(
        message.from_user.id
    )

    if missing:

        bot.send_message(
            message.chat.id,
            force_join_message(
                missing
            ),
            reply_markup=force_join_keyboard(
                missing
            )
        )

        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.send_message(
            message.chat.id,
            """
<b>🆘 SUPPORT ID</b>

Support ID দিতে এই Format ব্যবহার করুন:

<code>/2 @riyadahmed6890</code>
"""
        )

        return

    support_id = parts[1].strip()

    if not support_id.startswith("@"):

        support_id = "@" + support_id

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "🆘 CONTACT SUPPORT",
            url="https://t.me/" +
            support_id.replace("@", "")
        )
    )

    bot.send_message(
        message.chat.id,
        f"""
<b>🆘 SUPPORT</b>

━━━━━━━━━━━━━━━━━━

Support ID:

<b>{html.escape(support_id)}</b>

নিচের Button চাপ দিয়ে
Support-এর সাথে যোগাযোগ করুন।
""",
        reply_markup=keyboard
    )


# ============================================================
# IDENTITY
# ============================================================

def is_identity_question(text):

    text = text.lower().strip()

    keywords = [
        "তোমাকে কে বানিয়েছে",
        "তোরে কে বানাইছে",
        "কে তোমাকে বানিয়েছে",
        "কে বানিয়েছে তোমাকে",
        "তোমারে কে বানাইছে",
        "তোমাকে কে তৈরি করেছে",
        "who made you",
        "who created you",
        "who built you"
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


def identity_answer():

    return """
আমি একজন AI সহকারী।

আমাকে তৈরি করেছে তনময় আহমেদ স্যার।
স্যার একজন Cyber Security Specialist।

আমি AMCA Cyber-এর একজন সহকারী AI।
""".strip()


# ============================================================
# RESPONSE EXTRACTOR
# ============================================================

def extract_response(data):

    if isinstance(data, str):

        text = data.strip()

        return text if text else None

    if isinstance(data, list):

        for item in data:

            result = extract_response(
                item
            )

            if result:
                return result

        return None

    if not isinstance(data, dict):
        return None

    fields = [
        "response",
        "answer",
        "message",
        "result",
        "content",
        "text",
        "output",
        "generated_text"
    ]

    for field in fields:

        value = data.get(field)

        if isinstance(value, str):

            value = value.strip()

            if value:
                return value

    for key in [
        "data",
        "result",
        "response",
        "choices"
    ]:

        nested = data.get(key)

        if isinstance(
            nested,
            (dict, list)
        ):

            result = extract_response(
                nested
            )

            if result:
                return result

    return None


# ============================================================
# CLEAN RESPONSE
# ============================================================

def clean_response(text):

    if not text:
        return None

    text = str(text).strip()

    if "</think>" in text:

        text = text.split(
            "</think>",
            1
        )[1].strip()

    if "<think>" in text and "</think>" not in text:
        return None

    if not text:
        return None

    text = text.replace(
        "<script",
        "&lt;script"
    )

    return text


# ============================================================
# CALL API
# ============================================================

def call_api(api, question):

    name = api.get(
        "name",
        "Unknown"
    )

    url = api.get("url")

    if not url:
        return None

    try:

        params = {
            "q": question
        }

        prompt = api.get(
            "prompt",
            ""
        )

        if prompt:
            params["prompt"] = prompt

        with data_lock:

            DATA.setdefault(
                "stats",
                {}
            )

            DATA["stats"][
                "api_requests"
            ] = DATA["stats"].get(
                "api_requests",
                0
            ) + 1

        started = time.perf_counter()

        response = requests.get(
            url,
            params=params,
            timeout=API_TIMEOUT,
            headers={
                "User-Agent":
                "Premium-MultiAI-Bot/2.0"
            }
        )

        elapsed = (
            time.perf_counter()
            - started
        )

        if response.status_code != 200:

            print(
                f"[{name}] HTTP "
                f"{response.status_code} "
                f"{elapsed:.2f}s"
            )

            return None

        try:
            data = response.json()

        except Exception:
            data = response.text

        answer = extract_response(
            data
        )

        answer = clean_response(
            answer
        )

        if not answer:
            return None

        print(
            f"[SUCCESS] {name} "
            f"{elapsed:.2f}s"
        )

        return {
            "api": name,
            "answer": answer,
            "time": elapsed
        }

    except requests.exceptions.Timeout:

        print(
            f"[TIMEOUT] {name}"
        )

    except requests.exceptions.RequestException as e:

        print(
            f"[REQUEST ERROR] "
            f"{name}: {e}"
        )

    except Exception as e:

        print(
            f"[API ERROR] "
            f"{name}: {e}"
        )

    return None


# ============================================================
# PARALLEL AI
# ============================================================

def ask_ai(question):

    with api_lock:

        enabled_apis = [
            dict(api)
            for api in APIS
            if api.get(
                "enabled",
                True
            )
        ]

    if not enabled_apis:
        return None

    executor = ThreadPoolExecutor(
        max_workers=min(
            MAX_WORKERS,
            len(enabled_apis)
        )
    )

    futures = []

    try:

        for api in enabled_apis:

            futures.append(
                executor.submit(
                    call_api,
                    api,
                    question
                )
            )

        for future in as_completed(
            futures
        ):

            try:

                result = future.result()

            except Exception as e:

                print(
                    "[FUTURE ERROR]",
                    e
                )

                continue

            if result:

                for other in futures:

                    if other != future:
                        other.cancel()

                return result

    finally:

        try:

            executor.shutdown(
                wait=False,
                cancel_futures=True
            )

        except TypeError:

            executor.shutdown(
                wait=False
            )

    return None


# ============================================================
# SEND ANSWER
# ============================================================

def send_answer(
    chat_id,
    result
):

    api_name = html.escape(
        result["api"]
    )

    answer = result["answer"]

    elapsed = result["time"]

    text = (
        f"🤖 <b>{api_name}</b>\n"
        f"⚡ <b>{elapsed:.2f}s</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"{answer}"
    )

    limit = 3900

    if len(text) <= limit:

        bot.send_message(
            chat_id,
            text
        )

        return

    for start in range(
        0,
        len(text),
        limit
    ):

        bot.send_message(
            chat_id,
            text[
                start:
                start + limit
            ]
        )


# ============================================================
# USER TEXT
# ============================================================

@bot.message_handler(
    content_types=["text"]
)
def user_message(message):

    user_id = message.from_user.id

    # Menu buttons
    menu_buttons = [
        "🤖 AI CHAT",
        "👤 PROFILE",
        "🔗 REFER & EARN",
        "📊 MY STATS",
        "ℹ️ ABOUT",
        "🆘 SUPPORT"
    ]

    if message.text in menu_buttons:
        return

    # Commands
    if message.text.startswith("/"):
        return

    # Block
    if is_blocked(user_id):

        bot.send_message(
            message.chat.id,
            "🚫 আপনি এই Bot ব্যবহার করতে পারবেন না।"
        )

        return

    # Force Join
    missing = check_force_join(
        user_id
    )

    if missing:

        bot.send_message(
            message.chat.id,
            force_join_message(
                missing
            ),
            reply_markup=force_join_keyboard(
                missing
            )
        )

        return

    question = message.text.strip()

    if not question:
        return

    add_user(user_id)

    with data_lock:

        DATA["stats"]["messages"] = (
            DATA["stats"].get(
                "messages",
                0
            ) + 1
        )

    save_data()

    # Identity
    if is_identity_question(
        question
    ):

        bot.send_message(
            message.chat.id,
            identity_answer()
        )

        with data_lock:

            DATA["stats"]["success"] = (
                DATA["stats"].get(
                    "success",
                    0
                ) + 1
            )

        save_data()

        return

    chat_id = message.chat.id

    try:

        bot.send_chat_action(
            chat_id,
            "typing"
        )

    except Exception:
        pass

    waiting = bot.send_message(
        chat_id,
        "⚡ <b>AI Processing...</b>\n\n"
        "🚀 Searching the fastest AI..."
    )

    result = ask_ai(
        question
    )

    try:

        bot.delete_message(
            chat_id,
            waiting.message_id
        )

    except Exception:
        pass

    if result:

        with data_lock:

            DATA["stats"]["success"] = (
                DATA["stats"].get(
                    "success",
                    0
                ) + 1
            )

        save_data()

        send_answer(
            chat_id,
            result
        )

    else:

        with data_lock:

            DATA["stats"]["failed"] = (
                DATA["stats"].get(
                    "failed",
                    0
                ) + 1
            )

        save_data()

        bot.send_message(
            chat_id,
            """
❌ <b>AI Response পাওয়া যায়নি</b>

সব enabled AI বর্তমানে
Unavailable অথবা Timeout করেছে।

🔄 কিছুক্ষণ পরে আবার চেষ্টা করুন।
""",
            reply_markup=main_menu()
        )


# ============================================================
# ERROR HANDLER
# ============================================================

@bot.message_handler(
    content_types=[
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "sticker",
        "animation",
        "location",
        "contact"
    ]
)
def unsupported_message(message):

    missing = check_force_join(
        message.from_user.id
    )

    if missing:

        bot.send_message(
            message.chat.id,
            force_join_message(
                missing
            ),
            reply_markup=force_join_keyboard(
                missing
            )
        )

        return

    bot.send_message(
        message.chat.id,
        """
⚠️ <b>Text Message ব্যবহার করুন।</b>

AI-কে প্রশ্ন করতে আপনার
প্রশ্নটি Text হিসেবে পাঠান।
""",
        reply_markup=main_menu()
    )


# ============================================================
# RUNNER
# ============================================================

def run_bot():

    print()
    print("=" * 60)
    print("       PREMIUM MULTI AI TELEGRAM BOT")
    print("=" * 60)
    print("AI APIs       :", len(APIS))
    print("Force Join    :", len(FORCE_CHANNELS))
    print("Support       :", SUPPORT_USERNAME)
    print("Workers       :", MAX_WORKERS)
    print("Timeout       :", API_TIMEOUT)
    print("Users         :", total_users())
    print("Mode          : PARALLEL")
    print("Response      : FIRST VALID")
    print("Status        : ONLINE")
    print("=" * 60)
    print()

    while True:

        try:

            print(
                "[INFO] Removing webhook..."
            )

            bot.delete_webhook(
                drop_pending_updates=True
            )

            time.sleep(1)

            print(
                "[INFO] Starting polling..."
            )

            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=30,
                skip_pending=True,
                allowed_updates=[
                    "message",
                    "callback_query"
                ]
            )

        except KeyboardInterrupt:

            print(
                "\n[BOT] Stopped."
            )

            break

        except Exception as e:

            print(
                "[BOT ERROR]",
                e
            )

            print(
                "[BOT] Restarting..."
            )

            time.sleep(5)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    run_bot()