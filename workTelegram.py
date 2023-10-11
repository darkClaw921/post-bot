import os
import telebot
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pprint import pprint
from chat import GPT
from datetime import datetime
import workYDB
from loguru import logger
import sys
from createKeyboard import *
from helper import *
from workRedis import *

from questions import questionNewProject

load_dotenv()
isDEBUG = True

logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
logger.add("workTelegram.log", rotation="50 MB")
# gpt = GPT()
# GPT.set_key(os.getenv('KEY_AI'))
bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
sql = workYDB.Ydb()

TYPE_QUESTIONS = {'newProject': questionNewProject,}
                #   'evroShtak':questionEvroShtak} 
URL_USERS = {}
QUESTS_USERS = {}
COUNT_QUESTS_USER={}
PROMT_URLS = {'post': '',
            'stories':''}
USERS_ANSWER_GPT={}
# MODEL_URL= 'https://docs.google.com/document/d/1M_i_C7m3TTuKsywi-IOMUN0YD0VRpfotEYNp1l2CROI/edit?usp=sharing'
# #gsText, urls_photo = sheet.get_gs_text()
# #print(f'{urls_photo=}')
# model_index=gpt.load_search_indexes(MODEL_URL)
# # model_project = gpt.create_embedding(gsText)
# PROMT_URL = 'https://docs.google.com/document/d/10PvyALgUYLKl-PYwwe2RZjfGX5AmoTvfq6ESfemtFGI/edit?usp=sharing'
# model= gpt.load_prompt(PROMT_URL)

# PROMT_URL_SUMMARY ='https://docs.google.com/document/d/1XhSDXvzNKA9JpF3QusXtgMnpFKY8vVpT9e3ZkivPePE/edit?usp=sharing'
# #PROMT_PODBOR_HOUSE = 'https://docs.google.com/document/d/1WTS8SQ2hQSVf8q3trXoQwHuZy5Q-U0fxAof5LYmjYYc/edit?usp=sharing'





@bot.message_handler(commands=['addmodel'])
def add_new_model(message):
    sql.set_payload(message.chat.id, 'addmodel')
    bot.send_message(message.chat.id, 
        "Пришлите ссылку model google document и через пробел название модели (model1). Не используйте уже существующие названия модели\n Внимани! конец ссылки должен вылядить так /edit?usp=sharing",)


@bot.message_handler(commands=['addpromt'])
def add_new_model(message):
    sql.set_payload(message.chat.id, 'addpromt')
    bot.send_message(message.chat.id, 
        "Пришлите ссылку promt google document и через пробел название промта (promt1). Не используйте уже существующие названия модели\n Внимани! конец ссылки должен вылядить так /edit?usp=sharing",)
    

@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    username = message.from_user.username
    row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
    sql.create_table(str(message.chat.id), row)
    row = {'id': message.chat.id, 'nickname':username, 'payload': ''}
    sql.replace_query('user', row)
    
    text = """Здравствуйте, я AI ассистент """
    bot.send_message(message.chat.id, text, 
                     parse_mode='markdown',
                     reply_markup= create_menu_keyboard())


@bot.message_handler(commands=['restart'])
def restart_modal_index(message):
    global model_index, model 
    model_index=gpt.load_search_indexes(MODEL_URL)
    #url = 'https://docs.google.com/document/d/1f4GMt2utNHsrSjqwE9tZ7R632_ceSdgK6k-_QwyioZA/edit?usp=sharing'
    #model= gpt.load_prompt(url)
    model= gpt.load_prompt(PROMT_URL)
    bot.send_message(message.chat.id, 'Обновлено', 
                     parse_mode='markdown',
                     reply_markup= create_menu_keyboard())

@bot.message_handler(commands=['context'])
def send_button(message):
    global URL_USERS
    URL_USERS={}
    payload = sql.get_payload(message.chat.id)

    #answer = gpt.answer(validation_promt, context, temp = 0.1)
    sql.delete_query(message.chat.id, f'MODEL_DIALOG = "{payload}"')
    sql.set_payload(message.chat.id, ' ')
    #bot.send_message(message.chat.id, answer)
    clear_history(message.chat.id)
    bot.send_message(message.chat.id, 
        "Контекст сброшен",reply_markup=create_menu_keyboard(),)

    

    #create_lead_and_attach_file([],userID)


def my_project(userID):
    try:
            projects = sql.select_query('project', f'user_id = {userID}') 
    except:
        bot.send_message(userID,'Опа, похоже кто-то жмет туда куда не следует') 
    dic = {}
    for project in projects:
        dic.setdefault(project['name'], f"project_{project['time_epoh']}")

    bot.send_message(userID,'Список проектов',reply_markup=create_inlinekeyboard_is_row(dic) )

def create_content(typeContent, userID):
    global USERS_ANSWER_GPT
    projectID = sql.get_project_id(userID)
    project = sql.select_query('project',f'time_epoh={projectID}')[0] 
    projectName = project['name']
    promtURL = PROMT_URLS[typeContent]
    #promt load
    #gpt answer
    answerGPT = 'answerGPT'
    createContent = ''
    keyboard=keyboard_create_content(typeContent)
    bot.send_message(userID, f'Ваш контент: {answerGPT}',reply_markup=keyboard)
    USERS_ANSWER_GPT[userID]=answerGPT
    sql.set_payload(userID, f'contentDone_{projectID}_{typeContent}')
    

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(callFull):
    global URL_USERS, QUESTS_USERS,TYPE_QUESTIONS,COUNT_QUESTS_USER, USERS_ANSWER_GPT
    userID = callFull.message.chat.id
    call = callFull.data.split('_')
    logger.debug(f'{call=}')
    projectID = sql.get_project_id(userID)
    
    message_id = callFull.message.message_id
    chat_id = callFull.message.chat.id
    # if call[0] == 'type':
    # promtURLpost = ''
    # promtURLstories = ''
    # bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Новый текст сообщения")
    
    
    if call[0] == 'project':
        
        project = sql.select_query('project',f'time_epoh={call[1]}')[0]
        sql.set_payload(userID, f'projectEnter_{call[1]}')
        sql.set_project_id(userID, f'{call[1]}')

        text = f"""Проект: {project['name']}"""
        keyboard = keyboard_menu_project()
        bot.send_message(userID, text=text, reply_markup=keyboard)
        # keyboard = keyboard_type_content()
        bot.answer_callback_query(callFull.id) 

        return 0
    
    if call[0] == 'contenPlan':
        if call[1] == 'create':
            keyboard = keyboard_type_content()
            bot.send_message(userID, text='Какой тип контента хотите создать?', reply_markup=keyboard) 
            # sql.set_payload(userID, 'content_plan')
            pass
        if call[1] == 'now':
            pass
    
    if call[0] == 'menu':
        if call[1] == 'smm':
            keyboard = keyboard_smm_menu(project_id=projectID)
            bot.send_message(userID, text='Меню настройки SMM', reply_markup=keyboard)
            
        if call[1] == 'contentPlan':
            keyboard = keyboard_content_plan(project_id=projectID)
            bot.send_message(userID, text='Меню контент-плана', reply_markup=keyboard) 
        
        if call[1] == 'storitaling':
            pass
        if call[1] == 'selectProject':
            my_project(userID)
     
        bot.answer_callback_query(callFull.id) 
    
    if call[0] == 'smm':

        sqlColumn = call[1]
        url = sql.select_query('project', f'time_epoh = {projectID}')[0][sqlColumn]
        keyboard = keyboard_edit(sqlColumn, call[0])
        bot.send_message(userID, text=f'Текущие значение: {url}', reply_markup=keyboard)            

    if call[0] == 'edit':
        bot.send_message(userID, text=f'Пришлите новое значение',)            
        sql.set_payload(userID,f'edit_{call[1]}')


        
        
    if call[0] == 'contentCreate':
        sql.set_payload(userID, 'create_content')
        create_content(call[1],userID)
        bot.answer_callback_query(callFull.id)
        return 0
    
    if call[0] == 'create':
        
        if call[1] == 'done':
            row = {
                'time_epoh':time_epoch(),
                'project_id':projectID,
                'text': USERS_ANSWER_GPT[userID],
                'type_content': call[1]
            }
            sql.insert_query('content', rows=row)
            bot.send_message(userID, 'Ваш контент сохранен',reply_markup=create_menu_keyboard())
            # bot.answer_callback_query(callFull.id)
            pass
            #save last message gpt
        if call[1] == 'again':
            create_content(call[2],userID)
            # bot.answer_callback_query(callFull.id)
            pass
    bot.answer_callback_query(callFull.id)

    


@bot.message_handler(content_types=['text'])
@logger.catch
def any_message(message):
    global URL_USERS, QUESTS_USERS,TYPE_QUESTIONS,COUNT_QUESTS_USER
    #print('это сообщение', message)
    #text = message.text.lower()
    text = message.text.lower()
    userID= message.chat.id
    # dicVOLODIA= {message.text.upper(): max(lambda: message.body[::-1] / len(message))}
    username = message.from_user.username
    payload = sql.get_payload(userID)

    if payload.startswith('edit'):
        projectID = sql.get_project_id(userID)
        row = {
            payload.split('_')[1]: text
        }
        sql.update_query('project',row,f'time_epoh={projectID}')
        bot.send_message(userID, 'Значание сохранено',reply_markup=keyboard_menu_project()) 
        sql.set_payload(userID,'')
        return 0
    
    

    if text == 'добавить новый проект':
        sql.set_payload(userID, 'quest_1_newProject') 
        payload='quest_1_newProject'
        
        try:
            QUESTS_USERS[userID].append([])
        except:
            QUESTS_USERS.setdefault(userID,[])
        
        try:
            COUNT_QUESTS_USER[userID]['real'] += 1  
        except:
            COUNT_QUESTS_USER.setdefault(userID, {
                                                 'real': 1,
                                                 'profNastil': 1,
                                                 'evroShtak':1})
        numberZabor = COUNT_QUESTS_USER[userID]['real'] 
        bot.send_message(userID,f'Пожалуйста заполните все вопросы',)
        # return 0
    
    if payload.startswith('quest'):
        if text != 'добавить новый проект':
            QUESTS_USERS[userID].append(text)
        quest = payload.split('_')[1]
        logger.debug(f'{quest=}')
        logger.debug(f'{text=}')
        typeQuest = payload.split('_')[2]
        listQuestions = TYPE_QUESTIONS[typeQuest]
        try:
            bot.send_message(userID,listQuestions[quest]['text'],reply_markup=listQuestions[quest]['keyboard']) 
        except Exception as e:
            # Кончились вопросы
            row= {
                'time_epoh': time_epoch(),
                'user_id': userID,
                'name': QUESTS_USERS[userID][0],
                'prop1': QUESTS_USERS[userID][1],
                'prop2': QUESTS_USERS[userID][2],
                'prop3': QUESTS_USERS[userID][3],
            }
            sql.replace_query('project', row)
            bot.send_message(userID,f'ваши ответы {QUESTS_USERS[userID]}',)
            sql.set_payload(userID, '') 
            return 0
        
        print(f'{int(quest)=} {len(listQuestions)=}')
        
        # if int(quest) == len(listQuestions)+1:
        #         sql.set_payload(userID, 'quest_0') 
        #         return 0
        
        if int(quest) == len(listQuestions)+1:
            bot.send_message(userID,'Спасибо за ответы, мы просчитаем Ваш проект и свяжемся с вами')
            sql.set_payload(userID, 'exit')
        else:    
            sql.set_payload(userID, f'quest_{int(quest)+1}_{typeQuest}')

        return 0 
    
    if text == 'мои проекты':
        my_project(userID)
        return 0 

    add_message_to_history(userID, 'user', text)
    history = get_history(str(userID))
    logger.info(f'история {history}')

    #для теста почему-то иногда бывыет битая ссылка
    try:
        logger.info(f'{PROMT_URL}')
        model= gpt.load_prompt(PROMT_URL) 
    except:
        model= gpt.load_prompt(PROMT_URL) 

    lastMessage = history[-1]['content'] 
    keyboard = keyboard_create_content(payload.split('_')[2])

    try:
        if text == 'aabb':
            #принудительная саммари диалога
            1/0
        answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, lastMessage+text, history, model_index,temp=0.5, verbose=0)

        logger.info(f'ответ сети если нет ощибок: {answer}')
    except Exception as e:
        #саммари если превышено колтчество токенов
        if isDEBUG : bot.send_message(userID, e)
        history = summary(userID, e) 
        
        answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, text, history, model_index,temp=0.5, verbose=0)
        bot.send_message(message.chat.id, answer)
        add_message_to_history(userID, 'assistant', answer)

        return 0 
    
    USERS_ANSWER_GPT[userID]=answer
    add_message_to_history(userID, 'assistant', answer)

    
    logger.info(f'{message_content=}')
   
    bot.send_message(message.chat.id, answer,  parse_mode='markdown')
    
    now = datetime.now()+timedelta(hours=3)

    formatted_date = now.strftime("%Y-%m-%dT%H:%M:%S")
    
    
    row = {'all_price': float(allTokenPrice), 'all_token': int(allToken), 'all_messages': 1}
    sql.plus_query_user('user', row, f"id={userID}")
    
    
    # rows = {'time_epoch': time_epoch(),
    #         'MODEL_DIALOG': payload,
    #         'date': formatted_date,
    #         'id': userID,
    #         'nicname': username,
    #         #'token': username,
    #         #'token_price': username,
    #         'TEXT': f'Клиент: {text}'}
    # sql.insert_query('all_user_dialog',  rows)
    
    rows = {'time_epoch': time_epoch(),
            'MODEL_DIALOG': payload,
            'date': formatted_date,
            'id': userID,
            'nicname': username,
            'token': allToken,
            'token_price': allTokenPrice,
            'TEXT': f'Менеджер: {answer}'}
    sql.insert_query('all_user_dialog',  rows)


print(f'[OK]')
bot.infinity_polling()
