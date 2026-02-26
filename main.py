import logging
from aiogram import Bot, Dispatcher, executor, types
import openai
from dotenv import load_dotenv
import os

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Debug: make sure tokens are loaded
if not TELEGRAM_BOT_TOKEN or not GROQ_API_KEY:
    raise Exception("Telegram token or Groq API key not found in .env file!")

# ----------------------------
# Configure OpenAI / Groq API
# ----------------------------
openai.api_key = GROQ_API_KEY
openai.api_base = "https://api.groq.com/openai/v1"

# ----------------------------
# Configure logging
# ----------------------------
logging.basicConfig(level=logging.INFO)

# ----------------------------
# Initialize Telegram Bot
# ----------------------------
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot)

# ----------------------------
# Conversation memory
# ----------------------------
class Reference:
    def __init__(self):
        self.response = ""

reference = Reference()

def clear_past():
    reference.response = ""

# ----------------------------
# Telegram Handlers
# ----------------------------
@dispatcher.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.reply(
        "Hi 👋\nI am LLaMA 3.1 Telegram Bot!\n"
        "I can chat with you using LLaMA 3.1 AI model.\n"
        "Type anything to start the conversation.\n"
        "Commands:\n/start - Start bot\n/help - Help menu\n/clear - Clear conversation"
    )

@dispatcher.message_handler(commands=['help'])
async def helper(message: types.Message):
    help_text = """
Available commands:
/start - Start the bot
/clear - Clear conversation history
/help - Show this help menu
"""
    await message.reply(help_text)

@dispatcher.message_handler(commands=['clear'])
async def clear(message: types.Message):
    clear_past()
    await message.reply("✅ Conversation cleared.")

# ----------------------------
# Main chat handler
# ----------------------------
@dispatcher.message_handler()
async def chatgpt(message: types.Message):
    try:
        print(f">>> USER: {message.text}")

        # OpenAI v2.2.0 compatible call to Groq LLaMA 3.1
        response = openai.ChatCompletion.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "assistant", "content": reference.response},
                {"role": "user", "content": message.text}
            ]
        )

        reply = response['choices'][0]['message']['content']
        reference.response = reply

        print(f">>> LLaMA: {reply}")
        await bot.send_message(chat_id=message.chat.id, text=reply)

    except Exception as e:
        print("Error:", e)
        await message.reply("⚠️ Something went wrong. Please try again.")

# ----------------------------
# Start bot
# ----------------------------
if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=True)