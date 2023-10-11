import telebot
import os
from workYDB import Ydb    

bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
sql = Ydb()

@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    username = message.from_user.username
    row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
    sql.create_table(str(message.chat.id), row)
    #row = {'id': message.chat.id, 'payload': '',}
    row = {'id': abs(message.chat.id), 'model': '', 'promt': '','nicname':username, 'payload': ''}
    sql.replace_query('user', row)

    text = """Здравствуйте"""
    history = []
    answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, text, history, model_index,temp=0.5, verbose=0)
    add_message_to_history(message.chat.id, 'assistant', answer) 
    bot.send_message(message.chat.id, answer, 
                     parse_mode='markdown',)
                     #reply_markup= create_menu_keyboard())
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/')

bot.reply_to()