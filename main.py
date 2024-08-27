import os
import openai
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters
from telegram.constants import ChatAction
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
telegram_token = os.getenv('TELEGRAM_TOKEN')

# /start
async def start(update: Update, context: CallbackContext):
    user_first_name = update.message.from_user.first_name
    welcome_message = f"Здравствуйте, {user_first_name}! Введите URL адрес вебсайта для анализа его содержимого."
    await update.message.reply_text(welcome_message)

# Обработчик всех команд, начинающихся со знака "/"
async def handle_command(update: Update, context: CallbackContext):
    # Если команда не является "/start", перенаправляем её на функцию /start
    if update.message.text.startswith('/'):
        await start(update, context)

# process msg
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    user_language = update.message.from_user.language_code or 'en'  # Используем язык профиля пользователя

    # check are msg contains url?
    if "http" in user_message or "." in user_message:
        await update.message.chat.send_action(ChatAction.TYPING)
        prompt = f"Process user message and say what is industry type of website from user message: `{user_message}`. Respond in {user_language}."
    else:
        await update.message.chat.send_action(ChatAction.TYPING)
        error_message = "Ошибка: вы ввели не URL, введите заново."
        
        if user_language != 'ru':
            prompt = f"Translate the following error message into {user_language}: '{error_message}'."
            client = AsyncOpenAI(api_key=openai.api_key)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            error_message = response.choices[0].message.content.strip()
        
        await update.message.reply_text(error_message)
        return

    # async openai client
    client = AsyncOpenAI(api_key=openai.api_key)

    # get openai answer
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=500
    )
    
    reply = response.choices[0].message.content.strip()

    # send reply from openai to user
    await update.message.reply_text(reply)

def main():
    application = Application.builder().token(telegram_token).build()

    # process /start
    application.add_handler(CommandHandler('start', start))
    
    # process comamnds (/help and etc)
    application.add_handler(MessageHandler(filters.COMMAND, handle_command))

    # process any msg
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
