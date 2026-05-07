# ============================================
# Telegram Bot using Long Polling (Educational Purpose)
# Modules Used: requests, json, time
# ============================================

import requests
import json
import time

# ============================================
# CONFIG
# ============================================

BOT_TOKEN = "8204900696:AAG3mVSA5piMNagxCM1gArE1XH2elNzAuWM"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# External API URL (Leave Blank)
EXTERNAL_API_URL = "https://httpbin.org/get?number=""

# Dummy HTTPS Server URL (Educational Placeholder)
DUMMY_HTTPS_SERVER = "https://example.com"

# ============================================
# TELEGRAM FUNCTIONS
# ============================================

def send_message(chat_id, text, reply_markup=None):
    url = f"{API_URL}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Send Message Error:", e)


def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"

    params = {
        "timeout": 30
    }

    if offset:
        params["offset"] = offset

    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        print("Get Updates Error:", e)
        return {}


# ============================================
# REPLY KEYBOARD
# ============================================

reply_keyboard = {
    "keyboard": [
        [
            {
                "text": "📱 Phone Lookup"
            }
        ]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

# ============================================
# USER STATE STORAGE
# ============================================

waiting_for_number = {}

# ============================================
# EXTERNAL API CALL
# ============================================

def lookup_phone_number(phone_number):
    try:
        # Example:
        # https://your-api.com/?number=9876543210

        url = f"{EXTERNAL_API_URL}{phone_number}"

        response = requests.get(url)

        # Convert response to JSON
        data = response.json()

        # Pretty format JSON
        formatted = json.dumps(data, indent=4)

        return formatted

    except Exception as e:
        return json.dumps({
            "error": str(e)
        }, indent=4)


# ============================================
# MAIN BOT LOOP
# ============================================

def main():
    print("Bot Started...")

    offset = None

    while True:
        updates = get_updates(offset)

        if "result" in updates:

            for update in updates["result"]:

                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"]

                chat_id = message["chat"]["id"]

                text = message.get("text", "")

                # ====================================
                # /start command
                # ====================================

                if text == "/start":

                    welcome_text = (
                        "👋 Welcome to Phone Lookup Bot\n\n"
                        "Use the button below to start lookup."
                    )

                    send_message(
                        chat_id,
                        welcome_text,
                        reply_markup=reply_keyboard
                    )

                # ====================================
                # Phone Lookup Button
                # ====================================

                elif text == "📱 Phone Lookup":

                    waiting_for_number[chat_id] = True

                    send_message(
                        chat_id,
                        "📞 Send 10 digit mobile number:"
                    )

                # ====================================
                # Handle Mobile Number
                # ====================================

                elif waiting_for_number.get(chat_id):

                    # Validate Number
                    if text.isdigit() and len(text) == 10:

                        send_message(
                            chat_id,
                            "🔍 Searching..."
                        )

                        result = lookup_phone_number(text)

                        # Send formatted JSON inside <pre>
                        send_message(
                            chat_id,
                            f"<pre>{result}</pre>"
                        )

                    else:

                        send_message(
                            chat_id,
                            "❌ Invalid mobile number.\nPlease send a valid 10 digit number."
                        )

                    waiting_for_number[chat_id] = False

                # ====================================
                # Unknown Messages
                # ====================================

                else:

                    send_message(
                        chat_id,
                        "❗ Please use /start command."
                    )

        # Poll Delay
        time.sleep(1)


# ============================================
# RUN BOT
# ============================================

if __name__ == "__main__":
    main()
