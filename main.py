import telebot
import os
import time
import threading
from keep_alive import keep_alive

# --- Configuration ---
API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ADMIN_USER_ID_STR = os.environ.get('ADMIN_USER_ID')

# A check to ensure secrets are set on Render
if not all([API_TOKEN, ADMIN_USER_ID_STR]):
    raise ValueError("FATAL ERROR: Both TELEGRAM_BOT_TOKEN and ADMIN_USER_ID must be set in Render's Environment Variables.")

try:
    ADMIN_USER_ID = int(ADMIN_USER_ID_STR)
except ValueError:
    raise ValueError("FATAL ERROR: ADMIN_USER_ID must be a valid integer.")

bot = telebot.TeleBot(API_TOKEN)

# --- File Storage ---
# Using non-sequential, randomized keys to prevent users from guessing the next part.
FILES = {
    # --- Season 1 ---
    "got_s1p1_aK9sL2": { "file_ids": ["BQACAgUAAxkBAAMSaO3uOgfcHV-gX2wQnbVcNA9_CK4AAvgYAALD04BVgWp7S3LKzt42BA", "BQACAgUAAxkBAAMUaO3uOjTq2eCZpEvVoa_dFQw3Pr4AAgYZAALD04BVr0nJKIM1dAQ2BA", "BQACAgUAAxkBAAMQaO3uIGkpvqVbw9Yu01MiIAgrshYAAvkYAALD04BVg1Mk5bP0OIc2BA"] },
    "got_s1p2_zX7vB5": { "file_ids": ["BQACAgUAAxkBAAMVaO3uOtbU1dzQ3k1vWTOuZGidnJYAAhUZAAJPzaBVDU-DO9elIz42BA", "BQACAgUAAxkBAAMWaO3uOr6fUjlrt3gm5m8XQlebScwAAiwcAAJPzahV_GO7u5OK-fA2BA", "BQACAgUAAxkBAAMXaO3uOqCjaGa1SRgcoU9GO_pPvgEAAjQcAAJPzahVefloxxauffk2BA"] },
    "got_s1p3_nC6mJ8": { "file_ids": ["BQACAgUAAxkBAAMYA03uOr7ABfPefbeI8Hc3JDrNhYIAAjkcAAJPZahV1xvrdKt_Gmg2BA", "BQACAgUAAxkBAAMZA03u0vSeuyprQD9t7H9vxea_kQUAAj4cAAJPZahV5J4lUPqxuPc2BA", "BQACAgUAAxkBAAMaa03u0kpH8UYpId9oAAG5ZBYXZC8iAAJCHAACT82oVbgiCL3SaKrQNgQ", "BQACAgUAAxkBAAMba03uOr_acPkUkv5Xrn6H3AZPm-UAAkEcAJPZahVzahVsAVfBjjtII2BA"] },

    # Add other seasons and files here...
}


# --- Auto-Delete Scheduler ---

def schedule_message_deletion(chat_id, message_id):
    """Waits 10 minutes and then deletes the specified message."""
    time.sleep(600)  # 10 minutes = 600 seconds
    try:
        bot.delete_message(chat_id, message_id)
        print(f"Successfully deleted message {message_id} from chat {chat_id}.")
    except Exception as e:
        print(f"Could not delete message {message_id} from chat {chat_id}: {e}")


# --- Bot Command Handlers ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()

    if len(args) == 1:
        bot.reply_to(message, "👋 Welcome! Please use a special link from one of our channels to get a file.")
        return

    file_key = args[1]

    if file_key not in FILES:
        bot.reply_to(message, "❌ Invalid or expired file link.")
        return

    # The session limit check has been removed. We proceed directly to sending files.
    send_files_and_finalize(message, file_key)


def send_files_and_finalize(message, file_key):
    """Sends one or more files, adds warnings, and schedules deletion for each."""
    chat_id = message.chat.id

    try:
        file_id_list = FILES[file_key].get('file_ids', [])
        if not file_id_list:
            raise ValueError("No file_ids found for this key.")

        bot.send_message(chat_id, f"📂 Preparing your request... You will receive {len(file_id_list)} file(s).")
        time.sleep(2) # Small delay for a better user experience

        for i, file_id in enumerate(file_id_list):
            # --- Warning Message ---
            caption_text = (
                f"📎 File {i+1} of {len(file_id_list)}\n\n"
                f"⚠️ **Note:** This File/Video will be deleted in 10 mins ❌ (Due to Copyright Issues).\n\n"
                f"Please forward this to your **Saved Messages** and start your download there."
            )

            sent_message = bot.send_document(chat_id, file_id, caption=caption_text, parse_mode="Markdown")

            # --- Schedule Deletion for each file ---
            deletion_thread = threading.Thread(target=schedule_message_deletion, args=(chat_id, sent_message.message_id))
            deletion_thread.start()
            time.sleep(1) # Prevents Telegram from rate-limiting the bot

        # The user_usage tracking has been removed.
        bot.send_message(chat_id, "✅ All files have been sent.")

    except Exception as e:
        print(f"Error in send_files_and_finalize for key {file_key}: {e}")
        bot.send_message(chat_id, "❌ An error occurred while sending the files.")


@bot.message_handler(content_types=['document', 'video', 'audio'])
def get_file_id(message):
    """Admin-only function to get file IDs."""
    if message.from_user.id == ADMIN_USER_ID and message.chat.type == 'private':
        file_id = ""
        if message.document: file_id = message.document.file_id
        elif message.video: file_id = message.video.file_id
        elif message.audio: file_id = message.audio.file_id
        reply_text = f"New File ID Found!\n\n**ID:** `{file_id}`"
        bot.reply_to(message, reply_text, parse_mode="Markdown")


# --- Main Bot Execution ---
if __name__ == "__main__":
    print("🤖 Bot is starting...")
    keep_alive() # Starts the Flask web server in a thread
    print("✔️ Bot is now polling for messages.")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

