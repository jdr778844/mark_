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
    "got_s1p1_aK9sL2": { "file_ids": ["BQACAgUAAxkBAAMGaPkDKqSrNemKyZfLanX05t4hRSgAAvgYAALD04BVGnFxDjd7Xxg2BA","BQACAgUAAxkBAAMHaPkDKjQR9bAjF88hylR1564w6eAAAvkYAALD04BV3ZPXmQjmCWo2BA","BQACAgUAAxkBAAMIaPkDKvt9kW5QNrKTz_eCS716Rr8AAgYZAALD04BVBDtkp8flubM2BA"] },
    "got_s1p2_zX7vB5": { "file_ids": ["BQACAgUAAxkBAAMLaPkDKnz3oYPuinH4Sq4WXtvdnmYAAjQcAAJPzahVKEN7gM8uni82BA","BQACAgUAAxkBAAMKaPkDKkEbsaZQ_A-di1pkA6NfTSkAAiwcAAJPzahVkYtutAKdifw2BA","BQACAgUAAxkBAAMJaPkDKp6MnIa6d9H445u5S6YhOsgAAhUZAAJPzaBVU8w7PL4i6P42BA"] },
    "got_s1p3_nC6mJ8": { "file_ids": ["BQACAgUAAxkBAAMPaPkDKgUT_wGOmTP5C5fj3cRTmtgAAkEcAAJPzahVPBYg79_infE2BA","BQACAgUAAxkBAAMOaPkDKkrLL9kQ7LsOAV6dAAG-BrDVAAJCHAACT82oVfXJMEmM5uLcNgQ","BQACAgUAAxkBAAMNaPkDKrkM5JcrAwtIRF2IIyQ3WV0AAj4cAAJPzahVDhN2wrd83-E2BA","BQACAgUAAxkBAAMMaPkDKpdVbrHgYwodVAAB-bN8JAL2AAI5HAACT82oVSjprOrZjQo-NgQ"] },

    "got_s2p1_pQ5fG1": { "file_ids": ["BQACAgUAAxkBAANaaP0pQQABoDus6_4HqOihjgMR1VJsAALTGAACtrXBVdVVCtyBne6lNgQ", "BQACAgUAAxkBAANbaP0pQTpHHu0w-zE36-0kuekveowAAtQYAAK2tcFV9duqtJyPBCc2BA", "BQACAgUAAxkBAANcaP0pQbDSjRSN3sEXXG9aRGhU9_YAAtUYAAK2tcFVRkXrjDMHIOA2BA"] },
    "got_s2p2_kL4hT9": { "file_ids": ["BQACAgUAAxkBAANdaP0pQSfcKJocHedDuGx_iJ8qh50AAtcYAAK2tcFVrrx_vXHDzlI2BA", "BQACAgUAAxkBAANeaP0pQSGcEU9Ge2pjbJuX7SOeOX4AAtgYAAK2tcFVMJGMU9mzpQo2BA", "BQACAgUAAxkBAANfaP0pQWuuiMday41fbHpFKMj30PoAAtkYAAK2tcFV8usiXYH85Lg2BA"] },
    "got_s2p3_jM3sR7": { "file_ids": ["BQACAgUAAxkBAANgaP0pQZDvVsOUVlxky8Rufd3ekYcAAtoYAAK2tcFVvlyIHlgOEOg2BA", "BQACAgUAAxkBAANhaP0pQZZQDEvZ093JbBkKO1CF8HoAAtwYAAK2tcFVRo20Dag4IhM2BA", "BQACAgUAAxkBAANiaP0pQdhxd6pvFNntcAMPuZ7VH0wAAt0YAAK2tcFVTa0spER6dvM2BA", "BQACAgUAAxkBAANjaP0pQWveDB1yuDsBH94n3Hv7XGEAAt4YAAK2tcFVkFLfi2NGK2Y2BA"] },

    # --- Season 3 ---
    "got_s3p1_yU2vE4": { "file_ids": ["FILE_ID_FOR_S3_EP1", "FILE_ID_FOR_S3_EP2", "FILE_ID_FOR_S3_EP3"] },
    "got_s3p2_wA1zD3": { "file_ids": ["FILE_ID_FOR_S3_EP4", "FILE_ID_FOR_S3_EP5", "FILE_ID_FOR_S3_EP6"] },
    "got_s3p3_sB9xQ2": { "file_ids": ["FILE_ID_FOR_S3_EP7", "FILE_ID_FOR_S3_EP8", "FILE_ID_FOR_S3_EP9", "FILE_ID_FOR_S3_EP10"] },

    # --- Season 4 ---
    "got_s4p1_rF8wP1": { "file_ids": ["FILE_ID_FOR_S4_EP1", "FILE_ID_FOR_S4_EP2", "FILE_ID_FOR_S4_EP3"] },
    "got_s4p2_tG7vO9": { "file_ids": ["FILE_ID_FOR_S4_EP4", "FILE_ID_FOR_S4_EP5", "FILE_ID_FOR_S4_EP6"] },
    "got_s4p3_uH6uN8": { "file_ids": ["FILE_ID_FOR_S4_EP7", "FILE_ID_FOR_S4_EP8", "FILE_ID_FOR_S4_EP9", "FILE_ID_FOR_S4_EP10"] },

    # --- Season 5 ---
    "got_s5p1_iJ5tM7": { "file_ids": ["FILE_ID_FOR_S5_EP1", "FILE_ID_FOR_S5_EP2", "FILE_ID_FOR_S5_EP3"] },
    "got_s5p2_oK4sL6": { "file_ids": ["FILE_ID_FOR_S5_EP4", "FILE_ID_FOR_S5_EP5", "FILE_ID_FOR_S5_EP6"] },
    "got_s5p3_pL3rK5": { "file_ids": ["FILE_ID_FOR_S5_EP7", "FILE_ID_FOR_S5_EP8", "FILE_ID_FOR_S5_EP9", "FILE_ID_FOR_S5_EP10"] },

    # --- Season 6 ---
    "got_s6p1_qM2qJ4": { "file_ids": ["FILE_ID_FOR_S6_EP1", "FILE_ID_FOR_S6_EP2", "FILE_ID_FOR_S6_EP3"] },
    "got_s6p2_rN1pI3": { "file_ids": ["FILE_ID_FOR_S6_EP4", "FILE_ID_FOR_S6_EP5", "FILE_ID_FOR_S6_EP6"] },
    "got_s6p3_sO9oH2": { "file_ids": ["FILE_ID_FOR_S6_EP7", "FILE_ID_FOR_S6_EP8", "FILE_ID_FOR_S6_EP9", "FILE_ID_FOR_S6_EP10"] },

    # --- Season 7 ---
    "got_s7p1_tP8nG1": { "file_ids": ["FILE_ID_FOR_S7_EP1", "FILE_ID_FOR_S7_EP2", "FILE_ID_FOR_S7_EP3"] },
    "got_s7p2_uQ7mF9": { "file_ids": ["FILE_ID_FOR_S7_EP4", "FILE_ID_FOR_S7_EP5"] },
    "got_s7p3_vR6lE8": { "file_ids": ["FILE_ID_FOR_S7_EP6", "FILE_ID_FOR_S7_EP7"] },

    # --- Season 8 ---
    "got_s8p1_wS5kD7": { "file_ids": ["FILE_ID_FOR_S8_EP1", "FILE_ID_FOR_S8_EP2"] },
    "got_s8p2_xT4jC6": { "file_ids": ["FILE_ID_FOR_S8_EP3", "FILE_ID_FOR_S8_EP4"] },
    "got_s8p3_yU3iB5": { "file_ids": ["FILE_ID_FOR_S8_EP5", "FILE_ID_FOR_S8_EP6"] },

    # ---- 720p ----
# ---- 720p (Correct Order) ----

"st_s5p1_720p_rX3k5": {
  "file_ids": ["BQACAgUAAxkBAAOtaShfAV3Rjc883D5ailbs9-pEj2gAAnIXAAJY40FVuBDZ38m4ByM2BA"]
},
"st_s5p2_720p_tY4l6": {
  "file_ids": ["BQACAgUAAxkBAAOuaShfAa2RuOTL1cRhJ80PQCLNXdUAAnQXAAJY40FVXxGEqQJlV3E2BA"]
},
"st_s5p3_720p_uZ5m7": {
  "file_ids": ["BQACAgUAAxkBAAOvaShfAbfukgSQ1ox_Cdh48tpe3tsAAngXAAJY40FV58C3cOLk3qQ2BA"]
},
"st_s5p4_720p_vA6n8": {
  "file_ids": ["BQACAgUAAxkBAAOwaShfAdF8QLI7eewjQEYjFOE28JwAAnoXAAJY40FVSwpxiIf7X-82BA"]
},


# ---- 1080p (Correct Order) ----

"st_s5p1_1080p_rX3k5": {
  "file_ids": ["BQACAgUAAxkBAAOlaShVy8c9tyQYEaUGOs64N8qSBE0AApgWAAJY40FVUgxKazmczIo2BA"]
},
"st_s5p2_1080p_tY4l6": {
  "file_ids": ["BQACAgUAAxkBAAOmaShVy4RfX-HjrJWsUba3KhZl3SQAAp0WAAJY40FVxdSnQYGT0mc2BA"]
},
"st_s5p3_1080p_uZ5m7": {
  "file_ids": ["BQACAgUAAxkBAAOnaShVyyGsPYJPTP9UcZZF1pJXG9UAAp8WAAJY40FVSa0lmBNkh542BA"]
},
"st_s5p4_1080p_vA6n8": {
  "file_ids": ["BQACAgUAAxkBAAOoaShVyxZOKS8kPBjjQ3eT3pPHs6YAAqUWAAJY40FVF_FUM6ftOF02BA"]
}


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

# Note: The daily reset scheduler functions (reset_user_sessions, run_scheduler)
# and related imports/threads have been removed.

# --- Bot Command Handlers ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    # Removed user_id tracking
    args = message.text.split()

    if len(args) == 1:
        bot.reply_to(message, "👋 Welcome! Please use a special link from one of our channels to get a file.")
        return

    file_key = args[1]

    if file_key not in FILES:
        bot.reply_to(message, "❌ Invalid or expired file link.")
        return

    # Removed the check: if user_id in user_usage: ...

    send_files_and_finalize(message, file_key)


def send_files_and_finalize(message, file_key):
    """Sends one or more files, adds warnings, and schedules deletion for each."""
    # Removed user_id tracking from the start of this function
    chat_id = message.chat.id

    # Removed the final check: if user_id in user_usage: ...

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

        # Removed the line: user_usage[user_id] = True
        bot.send_message(chat_id, "✅ All files have been sent.") # Simplified final message

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
    # Removed the scheduler_thread start
    print("✔️ Bot is now polling for messages.")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

