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
from promtTXT import *
import speech_recognition as sr
from questions import questionNewProject
import uuid

load_dotenv()
isDEBUG = True

logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
logger.add("workTelegram.log", rotation="50 MB")
gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))
bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
sql = workYDB.Ydb()

TYPE_QUESTIONS = {'newProject': questionNewProject,}
                #   'evroShtak':questionEvroShtak} 
URL_USERS = {}
QUESTS_USERS = {}
COUNT_QUESTS_USER={}
PROMT_URLS = {'post': 'https://docs.google.com/document/d/1GWms8u_4xQmvbGwRCk61t73b8YFq3F0JIuHTPyE1KrU/edit?usp=sharing',
            'stories':''}
USERS_ANSWER_GPT={}
# MODEL_URL= 'https://docs.google.com/document/d/1M_i_C7m3TTuKsywi-IOMUN0YD0VRpfotEYNp1l2CROI/edit?usp=sharing'
# #gsText, urls_photo = sheet.get_gs_text()
# #print(f'{urls_photo=}')
# model_index=gpt.load_search_indexes(MODEL_URL)
# # model_project = gpt.create_embedding(gsText)
PROMT_URL_CREATE_CONTENT = 'https://docs.google.com/document/d/1lfcuIdcBx38zQVzAJv_XNniXoLAk-S1hj1GLuqU0qQs/edit?usp=sharing'
# model= gpt.load_prompt(PROMT_URL)
PROMT_URL_ONBORDING = 'https://docs.google.com/document/d/1qgkFSTg6co9-JvLRlUON2vqm7rLI0QTS_5SVFvsvWBw/edit?usp=sharing'
# PROMT_URL_SUMMARY ='https://docs.google.com/document/d/1XhSDXvzNKA9JpF3QusXtgMnpFKY8vVpT9e3ZkivPePE/edit?usp=sharing'
# #PROMT_PODBOR_HOUSE = 'https://docs.google.com/document/d/1WTS8SQ2hQSVf8q3trXoQwHuZy5Q-U0fxAof5LYmjYYc/edit?usp=sharing'


def send_long_message(userID, text):
    lstMessage=split_string_by_length(text, 3000)
    for message in lstMessage:
        bot.send_message(userID,text=message) 


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
    global QUESTS_USERS

    QUESTS_USERS[message.chat.id]= []
    username = message.from_user.username
    row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
    sql.create_table(str(message.chat.id), row)
    row = {'id': message.chat.id, 'nickname':username, 'payload': ''}
    sql.replace_query('user', row)
    projects = sql.select_query('project', f'user_id = {message.chat.id}')
    if projects == []:
        keyboard = create_start_keyboard(isFirst=True)
    else:
        keyboard = create_start_keyboard(isFirst=False)
    # QUESTS_USERS[userID] 
    text = """ Добро пожаловать в ContentCraft! 
Мы строим коммуникацию и делаем сторителлинг за вас, поэтому вам больше не надо ломать голову о тому, что и как выложить😇
Мы запоминаем всю информацию про бизнес, его особенности и делаем маркетинговый анализ, чтобы ваш контент достигал целей в два клика."""
    bot.send_message(message.chat.id, text, 
                     parse_mode='markdown',
                     reply_markup= keyboard)
    
    
    text = """Прежде чем начать генерировать контент вам необходимо ответить на несколько вопросов.
Эту информацию мы будем регулярно использовать в своей работе, поэтому постарайтесь отвечать подробно и конкретно, без расплывчатых и общих формулировок 🙌🏼"""    
    
    bot.send_message(message.chat.id, text, 
                     parse_mode='markdown',)
    
    keyboard = keyboard_yes_no()
    text = """Показать примеры ответов на вопросы?"""    
    
    bot.send_message(message.chat.id, text, 
                     parse_mode='markdown',
                     reply_markup= keyboard)


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


def my_project(userID, messageID):
    try:
        projects = sql.select_query('project', f'user_id = {userID}') 
    except:
        bot.edit_message_text(chat_id=userID,message_id=messageID,text='Опа, похоже кто-то жмет туда куда не следует') 
    dic = {}
    for project in projects:
        dic.setdefault(project['name'], f"project_{project['time_epoh']}")
    # if projects == []:
    #    bot.send_message(userID,text='У вас еще нет проектов',) 
    # else:
    bot.send_message(userID,text='Список проектов',reply_markup=create_inlinekeyboard_is_row(dic,'a') )



def delete_my_project(userID, messageID, projectID):
     
    sql.delete_query('project',where=f'time_epoh = {projectID}')
    sql.delete_query('ProfileDescription', where=f'idProfile = {projectID}')
    # return 0 
    projects = sql.select_query('project', f'user_id = {userID}')
    dic = {}
    for project in projects:
        dic.setdefault(project['name'], f"project_{project['time_epoh']}")
    bot.edit_message_text(chat_id=userID,message_id=messageID,text='Проект и все связанные сущности удалены',reply_markup=create_inlinekeyboard_is_row(dic) )




def create_content(typeContent, userID, messageID):

    global USERS_ANSWER_GPT
    clear_history(str(userID))
    projectID = sql.get_project_id(userID)
    project = sql.select_query('project',f'time_epoh={projectID}')[0] 
    subjectID = sql.get_subject_id(userID)
    projectName = project['name']
    # promtURL = PROMT_URLS[typeContent]
    #promt load
    #gpt answer
    promt = gpt.load_prompt(PROMT_URL_CREATE_CONTENT)
    # print(promt)
    promt = find_text_from_promt(forSubjectType=typeContent, text=promt)
    keys = find_key_words(promt)
    print(keys)
    answers = sql.get_answer_list_on(subjectID=subjectID, forProfileID=projectID)
    longMessage = get_long_message(userID)[0]
    # my_dict = {'a': 1, 'b': 2, 'c': 3}
    my_list = [{x:longMessage[x]} for x in longMessage]
    answers.extend(my_list)
    # answers.update(longMessage)
    # sql.get_answer_on
    for key in keys:
        for answer in answers:
            key1=key.replace('[','').replace(']','')
            if answer['tag'] == key1:
                promt = promt.replace(key,answer['answer'])
    promt = promt.replace('[StorytellingStructure]',StorytellingStructure)
    print(promt)
    # text = {"role": "user", "content": 'как можно точнее'}
    bot.send_message(userID, f'Генерация контента')
    
    
    
    answerGPT = gpt.answer(promt,[])[0]
    # answerGPT = 'answerGPT'
    add_message_to_history(userID, 'assistant', answerGPT)
    # answerGPT = 'answerGPT'
    createContent = ''
    keyboard=keyboard_create_content(typeContent)
    send_long_message(userID, answerGPT)
    # bot.send_message(userID, f'Ваш контент: {answerGPT}',reply_markup=keyboard)

    # bot.edit_message_text(chat_id=userID,message_id=messageID, text=f'Ваш контент: {answerGPT}',reply_markup=keyboard)
    USERS_ANSWER_GPT[userID]=answerGPT
    sql.set_payload(userID, f'contentDone_{projectID}_{typeContent}')

   

@bot.callback_query_handler(func=lambda call: True)
@logger.catch
def callback_inline(callFull):
    global URL_USERS, QUESTS_USERS,TYPE_QUESTIONS,COUNT_QUESTS_USER, USERS_ANSWER_GPT
    userID = callFull.message.chat.id
    call = callFull.data.split('_')
    logger.debug(f'{call=}')
    projectID = sql.get_project_id(userID)
    
    message_id = callFull.message.message_id
    chat_id = callFull.message.chat.id
    # backCall = sql.get_payload(userID,True)
    backCall = sql.get_call_back(userID)
    # if call[0] == 'type':
    # promtURLpost = ''
    # promtURLstories = ''
    # bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Новый текст сообщения")
    
    
    if call[0]=='project':
        if call[1] == 'add':
            sql.set_payload(userID, 'quest_1_newProject') 
            payload='quest_1_newProject'
            
            COUNT_QUESTS_USER[userID] = 1

            bot.send_message(userID,f'Название проекта')
            return 0
        
        payload = sql.get_payload(userID)
        project = sql.select_query('project',f'time_epoh={call[1]}')[0]
        sql.set_payload(userID, f'project_{call[1]}')
        sql.set_project_id(userID, f'{call[1]}')
        # project['id']
        # sql.select_query('asdas', where answer == 'asdf' and project_id == 1234,)
        text = f"""Проект: {project['name']}"""
        keyboard = keyboard_menu_project(typeMenu=payload)
    
        bot.edit_message_text(chat_id=userID,message_id=message_id, text=text, reply_markup=keyboard)
        # keyboard = keyboard_type_content()
        sql.set_call_back(userID,callFull.data) 
        bot.answer_callback_query(callFull.id) 
    
    if call[0] == 'yes':
        if call[1] == 'start':
            bot.send_message(userID,f'Пример воросов:')
            keyboard = keyboard_yes_no('project')
            bot.send_message(userID,f'Хотите сразу добавить новый проект?', reply_markup=keyboard)
            
        else:
            callFull.data='project_add'
            callback_inline(callFull=callFull)
        
        bot.answer_callback_query(callFull.id)
        return 0
     
    if call[0] == 'no':
        if call[1] == 'start':
            keyboard = keyboard_yes_no('project')
            bot.send_message(userID,f'Хотите сразу добавить новый проект?', reply_markup=keyboard)
        else: 
            bot.send_message(userID,f'Хорошо, вы можете добавить проект в любой момент из главного меню', )
            # my_project(userID=userID, messageID=message_id)
            # callback_inline(callFull=callFull)
        
        bot.answer_callback_query(callFull.id)
        return 0
        #  bot.send_message(userID,f'Пример воросов:')     

    if call[0] == 'contenPlan':
        # keyboard = keyboard_type_content()
        if call[1] == 'create':
            # keyboard = keyboard_type_content()
            # bot.send_message(userID, text='Какой тип контента хотите создать?', reply_markup=keyboard)
            # keyboard = create_keyboard_menu_from_sql(forSubjectType='content' , backCall=backCall, nameStartCallback='contentCreate') 
            keyboard = create_keyboard_menu_from_sql(forSubjectType='content' , backCall=backCall, ) 
            bot.edit_message_text(chat_id=userID,message_id=message_id, text='Какой тип контента хотите создать?', reply_markup=keyboard) 
            # sql.set_payload(userID, 'content_plan')
        
        if call[1] == 'now':
            # payload = sql.get_payload(userID).split('_')[2]
            #сделать для каждого отдельно
            keyboard = create_keyboard_menu_from_sql(forSubjectType='content' , backCall=backCall, nameStartCallback='contentGet') 
            bot.edit_message_text(chat_id=userID,message_id=message_id, text='Какой тип контента хотите посмотреть?', reply_markup=keyboard) 

    if call[0] == 'storitaling':
        # keyboard = keyboard_type_content()
        if call[1] == 'create':
            keyboard = keyboard_type_content()
            # bot.send_message(userID, text='Какой тип контента хотите создать?', reply_markup=keyboard) 
            bot.edit_message_text(chat_id=userID,message_id=message_id, text='Какой тип контента хотите создать?', reply_markup=keyboard) 
            # sql.set_payload(userID, 'content_plan')
        
        if call[1] == 'now':
            payload = sql.get_payload(userID).split('_')[2]
            #сделать для каждого отдельно
            content = sql.select_query('content', f"project_id = {projectID} and type_content = '{payload}' ")[0]
            bot.send_message(userID,content['text'],)    
            pass
    
    if call[0] == 'menu':
        if call[1] == 'smm':
            # backCall = sql.get_payload(userID)
            # keyboard = keyboard_smm_menu(project_id=projectID)
            print(f'{backCall=}')
            if backCall == '':
                backCall = sql.get_payload(userID)
            print(f'{backCall=}')

            keyboard = create_keyboard_menu_from_sql('profileInfo' , backCall=f'project_{projectID}')
            bot.edit_message_text(chat_id=userID,message_id=message_id, text='Меню настройки SMM', reply_markup=keyboard)
            
        if call[1] == 'contentPlan':
            keyboard = keyboard_content_plan(project_id=projectID)
            bot.edit_message_text(chat_id=userID,message_id=message_id, text='Меню контент-плана', reply_markup=keyboard) 
        
        if call[1] == 'storitaling':
            keyboard = keyboard_storitaling(project_id=projectID)
            bot.edit_message_text(chat_id=userID,message_id=message_id, text='Меню сторителинга', reply_markup=keyboard) 
            
        if call[1] == 'selectProject':
            my_project(userID,message_id)
        
        if call[1] == 'deleteProject':
            delete_my_project(userID=userID,messageID=message_id ,projectID=projectID)
        

        sql.set_payload(userID,callFull.data)
        
        bot.answer_callback_query(callFull.id) 
    
    if call[0] == 'profileInfo':

        
        subjectsCallback = call[1]
        subjectID = sql.select_query('SubjectsOfDescription',f"callback = '{subjectsCallback}'")[0]['id']
        # sql.get_answer_list_on(subjectID=subjectID, forProfileID=projectID)
        # questions = sql.get_question_list_on(subjectID=subjectID)
        keyboard = create_keyboard_question_from_sql(subjectID=subjectID, backCall=backCall) 
        # url = sql.select_query('project', f'time_epoh = {projectID}')[0][sqlColumn]
        # keyboard = keyboard_edit(sqlColumn, call[0])
        # bot.edit_message_text(chat_id=userID,message_id=message_id, text=f'Текущие значение: {url}', reply_markup=keyboard)            
        bot.edit_message_text(chat_id=userID,message_id=message_id, text=f'Выберите нужное', reply_markup=keyboard)            

    if call[0] == 'question':
        # backPayload = sql.set
        sql.set_payload(userID,callFull.data)
        questionID = int(call[1])
        
        try:
            oldAnswer = sql.get_answer_on(questionID=questionID,forProfileID=projectID)[0]['Answer']
        except:
            oldAnswer = ''
        
        backCall = sql.get_payload(userID,isBackPayload=True)
        keyboard = keyboard_edit(property=callFull.data,backCall=backCall)
        try:
            bot.edit_message_text(chat_id=userID,message_id=message_id, text=f'Текущие значение: \n{oldAnswer}', reply_markup=keyboard)            
        except:
            send_long_message(oldAnswer)

    if call[0] =='onbording':
        subjectID = call[1]
        # sql.set_subject_id(userID,subjectID) 
        # sql.set_payload()
        questions = sql.get_question_list_on(subjectID=subjectID)
        questions = create_dict_questions(questions)
        sql.set_subject_id(userID=userID, entity=subjectID)

        textQuestion = questions[1]['text']
        bot.send_message(userID,text=textQuestion)
        sql.set_payload(userID, 'quest_1')  
        COUNT_QUESTS_USER[userID] = 1

    if call[0] == 'edit':
        bot.edit_message_text(chat_id=userID,message_id=message_id, text=f'Пришлите новое значение',)            
        sql.set_payload(userID,f'edit_{call[1]}_{call[2]}')   
        
    if call[0] == 'contentCreate':
        clear_history(str(userID))
        # get_history(str(userID))
        sql.set_payload(userID, 'create_content')
        
        create_content(call[1],userID,message_id)
        bot.answer_callback_query(callFull.id)
        return 0
    
    if call[0] == 'create':
        
        if call[1] == 'done':
            row = {
                'time_epoh':time_epoch(),
                'project_id':projectID,
                'text': USERS_ANSWER_GPT[userID],
                'type_content': call[2]
            }
            sql.insert_query('content', rows=row)
            bot.edit_message_text(chat_id=userID,message_id=message_id,text='Ваш контент сохранен',reply_markup=keyboard_menu_project())
            # bot.answer_callback_query(callFull.id)
            pass
            #save last message gpt
        if call[1] == 'again':
            create_content(call[2],userID,message_id)
            # bot.answer_callback_query(callFull.id)
            pass
   
    if call[0] == 'content':
        if call[1] == 'post': # create
            subjectID = 6 
        
        if call[1] == 'stories': #create
            subjectID= 5
           

        sql.set_payload(userID,'quest_1')
        sql.set_subject_id(userID,subjectID)
        questions = sql.get_question_list_on(subjectID=subjectID)
        questions = create_dict_questions(questions)
        
        mes = maessageStartSubject[subjectID]
        bot.send_message(userID,text=mes)
        
        textQuestion = questions[1]['text']
        bot.send_message(userID,text=textQuestion) 
        COUNT_QUESTS_USER[userID] = 1 
    
    if call[0] == 'contentGet':
        if call[1] == 'post': # create
            subjectID =6
        
        if call[1] == 'stories': #create
            subjectID= 5

        contents = sql.select_query('content', f'project_id = {projectID} and type_content="{call[1]}"')
        text = ''
        # pprint(contents)
        for content in contents:
            # date = timestamp_to_date(content['time_epoh'],'%Y-%m-%d%H')
            text += f"""\n {content['text']} \n\n"""
        if text== '':
            bot.send_message(userID,"Похоже у вас еще нет контента =(") 
        else:
            bot.send_message(userID,text) 

    sql.set(userID=userID, what='content_create', entity=call[1])
    sql.set_call_back(userID,callFull.data)
    bot.answer_callback_query(callFull.id)

#TODO 
# a = {'[about the product]=': 'prod_info',
#      }

maessageStartSubject ={
    1:'Ответьте, пожалуйста, на несколько вопросов о целевой аудитории',
    2:'Ответьте, пожалуйста, на несколько вопросов для формирования тональности ведения блога',
    3:'Ответьте, пожалуйста, на несколько вопросов о продукте',
    5:'Ответьте, пожалуйста, на несколько вопросов для создания сториз.',
    6:'Ответьте, пожалуйста, на несколько вопросов для написания поста.',
    7:'Ответьте, пожалуйста, на несколько вопросов для начала'

}


def create_onbord_for(subjectID, userID, projectID, message_id,questionID):
    subject = {
        1: 'TargetAudience',
        2: 'ProductAdvantages',
        3: 'ToneOfVoice'
    }

    from promtTXT import target
    # bot.send_message(userID,text='Готово')
    # promt = gpt.load_prompt()
    subjectCallBack = sql.select_query('SubjectsOfDescription',f'id ={subjectID}')[0]['callback']
    promtAll = gpt.load_prompt(PROMT_URL_ONBORDING)
    # print(promt)
    logger.debug(f'{subjectCallBack=}')
    promt = find_text_from_promt(forSubjectType=subjectCallBack, text=promtAll)
    print(f'{promt=}')
    keys = find_key_words(promt)
    print(f'{keys=}') 

    answers = sql.get_answer_list_on(subjectID=subjectID, forProfileID=projectID)
    
    
    longMessage = get_long_message(userID)
    if longMessage == []:
        my_list = []
    else: 
        longMessage = longMessage[0]
        my_list = [{'tag':x, 'answer':longMessage[x]} for x in longMessage]
    answers.extend(my_list)
    pprint(answers)
    for key in keys:
        for answer in answers:
            key1=key.replace('[','').replace(']','')
            if answer['tag'] == key1:
                promt = promt.replace(key,answer['answer'])
    print(promt)
    # text = {"role": "user", "content": 'как можно точнее'}
    # bot.send_message(userID, f'Формирую описание ЦА…')
    bot.send_message(userID, f'Формирую описание проекта. Процесс может занять несколько минут')
    #TODO #NOTE
    answerGPT = gpt.answer(promt,[])[0]
    # answerGPT = "AnswerGPT"
    longMessage = get_long_message(userID)
    if longMessage == []:
        add_long_message(userID, {subject[subjectID]:answerGPT})
    else: 
        a = {subject[subjectID]: answerGPT}
        extendedDict = longMessage[0] | a
        print(f'{extendedDict=}')
        add_long_message(userID,extendedDict)
   


    print(f'{answerGPT=}')
    
    # answer = gpt.answer(PROMT_URL,history)[0]  
    send_long_message(userID, answerGPT)
    # bot.send_message(userID,text=answerGPT,) 
    # my_project(userID,message_id)
    answer = sql.get_answer_on(questionID=questionID, forProfileID=projectID) 
    # numQuestion = int(sql.get_payload(userID).split('_')[1])
    if answer == []:
        row = {
            'id':time_epoch(),
            'idProfile': sql.get_project_id(userID),
            # 'Answer': subjectCallBack,
            'Answer': answerGPT,
            'idQuestionList': questionID
        }
        sql.insert_query('ProfileDescription', rows=row)
    else:
        row = {
            'Answer': answerGPT,
        }
        sql.update_query('ProfileDescription', rows=row, where=f"idProfile = {projectID} and idQuestionList={questionID}")
    return 0 


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    text = message.text
    logger.debug(f'{text=}')
    filename = str(uuid.uuid4())
    file_name_full="voice/"+filename+".ogg"
    file_name_full_converted="ready/"+filename+".wav"
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name_full, 'wb') as new_file:
        new_file.write(downloaded_file)
    os.system("ffmpeg -i "+file_name_full+"  "+file_name_full_converted)
    text=recognise(file_name_full_converted)
    bot.reply_to(message, text)
    os.remove(file_name_full)
    os.remove(file_name_full_converted)
    # a = message.text
    print(f'{a=}')
    message.text = text
    # a = message.text
    # print(f'{a=}')

    # print(f'{message=}')
    any_message(message)

#status  null-просто вопровс generate-генерация гпт asnwerGTP-ответ от гпт 
@bot.message_handler(content_types=['text'])
@logger.catch
def any_message(message):
    global URL_USERS, QUESTS_USERS,TYPE_QUESTIONS,COUNT_QUESTS_USER
    #print('это сообщение', message)
    #text = message.text.lower()
    text = message.text.lower()
    userID= message.chat.id
    message_id = message.message_id
    # print(message_id)
    # dicVOLODIA= {message.text.upper(): max(lambda: message.body[::-1] / len(message))}
    username = message.from_user.username
    payload = sql.get_payload(userID)
    projectID = sql.get_project_id(userID)
    subjectID= sql.get_subject_id(userID)
    # text = asdlkasl;kfjlas;

    if text == 'управление проектами':
        my_project(userID,message_id)
        sql.set_payload(userID,'control')

        return 0
    
    if text == 'генерация':
        my_project(userID,message_id)
        sql.set_payload(userID,'content') 
        return 0
    
    if payload.startswith('edit'):
        projectID = sql.get_project_id(userID)
        questionID = int(payload.split('_')[2])
        type = payload.split('_')[1]
        if type == 'question':
            row = {
                'Answer': text
            }
        else:
            row ={}
        oldAnswer = sql.get_answer_on(questionID=questionID,forProfileID=projectID)
        print(oldAnswer)
        if oldAnswer == []:
            row = {
                'Answer': text,
                'id': time_epoch(),
                'idProfile': projectID,
                'idQuestionList':questionID,
            }
            sql.insert_query('ProfileDescription',rows=row)
        else:
            sql.update_query('ProfileDescription',row,f'idProfile={projectID} and idQuestionList = {questionID}')
        bot.send_message(userID, 'Значание сохранено',reply_markup=keyboard_menu_project()) 
        sql.set_payload(userID,'')
        return 0
    
    


# SubjectType.profileInfo
    # subjectID = 1
    


    if text == 'добавить новый проект':
        sql.set_payload(userID, 'quest_1_newProject') 
        payload='quest_1_newProject'
        
        COUNT_QUESTS_USER[userID] = 1

        bot.send_message(userID,f'Название проекта',)
        return 0
    
    if payload.startswith('quest_1_newProject'):
        
        proID = time_epoch() 
        row= {
            'time_epoh': proID,
            'user_id': userID,
            'name': text,
        }
        sql.replace_query('project', row)
        bot.send_message(userID,f'Проект зарегистрирован',reply_markup=create_menu_keyboard())
        
        sql.set_payload(userID, '1quest_1') 
        sql.set_project_id(userID=userID, entity=proID)
        
        questions = sql.get_question_list_on(subjectID=7)
        questions = create_dict_questions(questions)
        sql.set_subject_id(userID=userID, entity=7)
        
        mes = maessageStartSubject[1]
        bot.send_message(userID,text=mes)
        
        textQuestion = questions[1]['text']
        bot.send_message(userID,text=textQuestion) 
        return 0

    

    #нужно для перехода в следующую цепочку вопросов
    if payload.startswith('1quest_1'):
        payload = 'quest_1'
        sql.set_payload(userID, 'quest_1')  


    if payload.startswith('quest'):
        numQuestion = int(payload.split('_')[1])
         
        # questions1 = sql.get_question_list_on(subjectID=subjectID)
        #TODO борать только вопросы с типом вопрос 
        # questions1 = sql.get_question_list_on(subjectID=subjectID)
        questions1 = sql.get_question_list_on(subjectID=subjectID, onlyQuestion=True)
        # questions2 = sql.get_question_list_on(subjectID=2)
        # questions3 = sql.get_question_list_on(subjectID=3)
        questions=questions1
        # questions.extend(questions2)
        # questions.extend(questions3)
        # pprint(questions)
        # try:
        questions = create_dict_questions(questions)
        typeQuestions = questions[numQuestion]['typeQuestion']

        idQuestions = questions[numQuestion]['id']
        logger.debug(f'ответ на {numQuestion} вопрос {text}')

        if numQuestion == len(questions):
            answer = sql.get_answer_on(questionID=idQuestions, forProfileID=projectID)
            if answer == []:
                row = {
                    'id':time_epoch(),
                    'idProfile': sql.get_project_id(userID),
                    'Answer': text,
                    # 'idQuestionList': numQuestion
                    'idQuestionList': idQuestions
                }
                sql.insert_query('ProfileDescription', rows=row)
            else:
                row = {
                    'Answer': text,
                }
                # sql.update_query('ProfileDescription', rows=row, where=f"idProfile = {projectID} and idQuestionList={numQuestion}") 
                sql.update_query('ProfileDescription', rows=row, where=f"idProfile = {projectID} and idQuestionList={idQuestions}")
            nameProject = sql.select_query('project', f'time_epoh={projectID}')[0]['name']
            
            bot.send_message(userID,text=f'Весь проект заполнен спасибо. Информацию о проекте вы можете посмотреть в разделе: Мои проекты / {nameProject} / Информация о проекте',)
            sql.set_payload(userID,f"")
            return 0

        if typeQuestions == 'generate' or numQuestion == len(questions):
        #NOTE 
        # if numQuestion == len(questions):
            # answer = sql.get_answer_on(questionID=numQuestion, forProfileID=projectID)
            answer = sql.get_answer_on(questionID=idQuestions, forProfileID=projectID)
            if answer == []:
                row = {
                    'id':time_epoch(),
                    'idProfile': sql.get_project_id(userID),
                    'Answer': text,
                    # 'idQuestionList': numQuestion
                    'idQuestionList': idQuestions
                }
                sql.insert_query('ProfileDescription', rows=row)
            else:
                row = {
                    'Answer': text,
                }
                # sql.update_query('ProfileDescription', rows=row, where=f"idProfile = {projectID} and idQuestionList={numQuestion}") 
                sql.update_query('ProfileDescription', rows=row, where=f"idProfile = {projectID} and idQuestionList={idQuestions}") 
            
            #TODO 
            #просто по последнему вопросу генерируем
            idQuestionsMinor = questions[numQuestion+1]['id']
            anySubject = [5,6]
            if subjectID in anySubject:
                # create_onbord_for(subjectID=subjectID,userID=userID,projectID=projectID, message_id=message_id, questionID=idQuestionsMinor)
                contentType = sql.get('content_create', userID)
                create_content(contentType,userID,message_id)
                sql.set_payload(userID, 'create_content')
                # create_onbord_for(subjectID=subjectID,userID=userID,projectID=projectID, message_id=message_id, questionID=idQuestionsMinor)
                return 0
            else:
                create_onbord_for(subjectID=subjectID,userID=userID,projectID=projectID, message_id=message_id, questionID=idQuestionsMinor)

            # bot.send_message(userID,text=textQuestion,)

            # sql.get
            #TODO 
            #и установать payload
            subjectID +=1
            sql.set_payload(userID,'quest_1')
            questions = sql.get_question_list_on(subjectID=subjectID)
            if questions == []:
                nameProject = sql.select_query('project', f'time_epoh={projectID}')[0]['name']
                bot.send_message(userID,text=f'Весь проект заполнен спасибо. Информацию о проекте вы можете посмотреть в разделе: Мои проекты / {nameProject} / Информация о проекте',)
                sql.set_payload(userID,f"")
                return 0
            
            mes = maessageStartSubject[subjectID]
            bot.send_message(userID,text=mes)
            # idQuestions = questions[1]['id'] 
            textQuestion = questions[0]['Question']
            bot.send_message(userID,text=textQuestion,)
            sql.set_subject_id(userID,subjectID)
            COUNT_QUESTS_USER[userID] = 1
            return 0

            #TODO
            #subjectID взять количество из базы потом 
        # if numQuestion !=1:
        # bot.send_message(userID,text=textQuestion,)
        # else:
        #     textQuestion = questions[2]['text']
        #     bot.send_message(userID,text=textQuestion,) 
        
        
        answer = sql.get_answer_on(questionID=idQuestions, forProfileID=projectID)
        
        if answer == []:
            row = {
                'id':time_epoch(),
                'idProfile': sql.get_project_id(userID),
                'Answer': text,
                # 'idQuestionList': numQuestion
                'idQuestionList': idQuestions
            }
            sql.insert_query('ProfileDescription', rows=row)
        else:
            row = {
                'Answer': text,
            }
            # sql.update_query('ProfileDescription', rows=row, where=f"idProfile = {projectID} and idQuestionList={numQuestion}")
            sql.update_query('ProfileDescription', rows=row, where=f"idProfile = {projectID} and idQuestionList={idQuestions}")
        
        COUNT_QUESTS_USER[userID] += 1
        try:
            textQuestion = questions[numQuestion+1]['text']
        except:
            bot.send_message(userID,text='весь проект заполнен спасибо',)
            sql.set_payload(userID,f"")
            return 0 
        
        bot.send_message(userID,text=textQuestion,)
        sql.set_payload(userID,f"quest_{COUNT_QUESTS_USER[userID]}")
        return 0
    
    add_message_to_history(userID, 'user', text)
    history = get_history(str(userID))
    logger.info(f'история {history}')

    #для теста почему-то иногда бывыет битая ссылка
    # try:
    #     logger.info(f'{PROMT_URL}')
    #     model= gpt.load_prompt(PROMT_URL) 
    # except:
    #     model= gpt.load_prompt(PROMT_URL) 

    lastMessage = history[-1]['content'] 
    # keyboard = keyboard_create_content(payload.split('_')[2])
    keyboard = None 
    promt = gpt.load_prompt(PROMT_URL_CREATE_CONTENT)
    subjectType = sql.get('content_create', userID)
    promt = find_text_from_promt(forSubjectType=subjectType, text=promt)
    print(f'{promt=}')
    try:
        keys = find_key_words(promt)
        print(f'{keys=}') 
        answers = sql.get_answer_list_on(subjectID=subjectID, forProfileID=projectID)

        for key in keys:
            for answer in answers:
                key1=key.replace('[','').replace(']','')
                if answer['tag'] == key1:
                    promt = promt.replace(key,answer['answer'])
        print(promt)
        promt = promt.replace('[StorytellingStructure]',StorytellingStructure)
    except:
        promt = 'ты помошник по генерации контена'
    try:
        if text == 'aabb':
            #принудительная саммари диалога
            1/0
        pprint(history)
        answer = gpt.answer(PROMT_URL_CREATE_CONTENT,history)[0]
        # answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, lastMessage+text, history, model_index,temp=0.5, verbose=0)

        logger.info(f'ответ сети если нет ощибок: {answer}')
    except Exception as e:
        #саммари если превышено колтчество токенов
        if isDEBUG : bot.send_message(userID, e)
        history = summary(userID, e) 
        answer = gpt.answer(PROMT_URL_CREATE_CONTENT,history)[0] 
        # answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, text, history, model_index,temp=0.5, verbose=0)
        bot.send_message(message.chat.id, answer, reply_markup=keyboard)
        add_message_to_history(userID, 'assistant', answer)

        return 0 
    
    USERS_ANSWER_GPT[userID]=answer
    add_message_to_history(userID, 'assistant', answer)

    
    # logger.info(f'{message_content=}')
   
    bot.send_message(chat_id=message.chat.id, text=answer,  parse_mode='markdown', reply_markup=keyboard)
    
    now = datetime.now()+timedelta(hours=3)

    formatted_date = now.strftime("%Y-%m-%dT%H:%M:%S")
    
    
    # row = {'all_price': float(allTokenPrice), 'all_token': int(allToken), 'all_messages': 1}
    # sql.plus_query_user('user', row, f"id={userID}")
    
    
    # rows = {'time_epoch': time_epoch(),
    #         'MODEL_DIALOG': payload,
    #         'date': formatted_date,
    #         'id': userID,s
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
            # 'token': allToken,
            # 'token_price': allTokenPrice,
            'token': 0,
            'token_price': 0,
            'TEXT': f'Менеджер: {answer}'}
    # sql.insert_query('all_user_dialog',  rows)

print(f'[OK]')
bot.infinity_polling()
