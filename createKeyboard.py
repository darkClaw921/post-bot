import telebot
from workYDB import Ydb
from helper import SubjectType
sql = Ydb()
def create_keyboard_is_row(rows: list):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    for row in rows:
        keyboard.row(row)
    return keyboard

def create_inlinekeyboard_is_row(rows: dict,type:str=None):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for text, callback in rows.items():
        keyboard.row(telebot.types.InlineKeyboardButton(text=text, callback_data=callback)) 
    if type is None:
        1+0
    else: 
        keyboard.row(telebot.types.InlineKeyboardButton(text='Добавить проект', callback_data='project_add'))  
    return keyboard

def create_menu_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    # keyboard.row('Добавить новый проект')
    keyboard.row('Мои проекты')
    return keyboard

def create_start_keyboard(isFirst:bool = True):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    if isFirst:
        keyboard.row('Добавить новый проект')
    else:
        keyboard.row('Добавить новый проект')
        keyboard.row('Мои проекты')
    return keyboard


def keyboard_type_content():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text='Пост', callback_data=f"contentCreate_post")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='Сторис', callback_data=f"contentCreate_stories")) 
    return keyboard

def keyboard_create_content(lastFix=''):
    #lastFix - имя проекта или id
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text='Давай еще разок', callback_data=f"create_again_{lastFix}")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='Сойдет', callback_data=f"create_done_{lastFix}")) 
    return keyboard

def keyboard_menu_project():
    #lastFix - имя проекта или id
    keyboard = telebot.types.InlineKeyboardMarkup()

    keyboard.row(telebot.types.InlineKeyboardButton(text='Генерация контента', callback_data=f"contenPlan_create")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='Готовый контент', callback_data=f"contenPlan_now")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='Информация о проекте', callback_data=f"menu_smm")) 
    # keyboard.row(telebot.types.InlineKeyboardButton(text='Настройки SMM', callback_data=f"menu_smm")) 
    # keyboard.row(telebot.types.InlineKeyboardButton(text='Контент-план', callback_data=f"menu_contentPlan")) 
    # keyboard.row(telebot.types.InlineKeyboardButton(text='Генерация контента', callback_data=f"menu_contentPlan")) 
    # keyboard.row(telebot.types.InlineKeyboardButton(text='Готовый контент', callback_data=f"menu_storitaling")) 
    # keyboard.row(telebot.types.InlineKeyboardButton(text='Сторителлинг', callback_data=f"menu_storitaling")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='Удалить проект', callback_data=f"menu_deleteProject")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='<<', callback_data=f"menu_selectProject")) 
    return keyboard

def keyboard_edit(property:str='', backCall=''):
    #property - название колонки в базе 

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text='Изменить', callback_data=f"edit_{property}")) 
    # можно передать тип меню а потом вернуть на шаг назад
    # keyboard.row(telebot.types.InlineKeyboardButton(text='<<', callback_data=f"menu_{typeMenu}")) 
    
    keyboard.row(telebot.types.InlineKeyboardButton(text='<<', callback_data=f"{backCall}")) 
    return keyboard

def keyboard_smm_menu(project_id:int):
    #callback должен называтся также как в базе
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text='Ссылка на профиль', callback_data=f"smm_url")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='Tone of Voice', callback_data=f"smm_tov")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='Цель SMM', callback_data=f"smm_target")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='ЦА', callback_data=f"smm_cha")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='Продукт', callback_data=f"smm_product")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='История', callback_data=f"smm_history")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='Рынок', callback_data=f"smm_market")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='<<', callback_data=f"project_{project_id}")) 
    return keyboard

def keyboard_content_plan(project_id:int):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text='Текущий', callback_data=f"contenPlan_now")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='Создать новый', callback_data=f"contenPlan_create")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='<<', callback_data=f"project_{project_id}")) 
    return keyboard

def keyboard_storitaling(project_id:int):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text='Текущий', callback_data=f"storitaling_now")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='Создать новый', callback_data=f"storitaling_create")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='<<', callback_data=f"project_{project_id}")) 
    return keyboard

def create_keyboard_menu_from_sql(forSubjectType:str,backCall:str='project', nameStartCallback = None):
    points = sql.select_query('SubjectsOfDescription', f"subjectsType = '{forSubjectType}'")
    dic = {}
    for point in points:
        if nameStartCallback is None:
            dic[point['name']]= f"{forSubjectType}_{point['callback']}"
        else:    
            dic[point['name']]= f"{nameStartCallback}_{point['callback']}"
            
    keyboard = create_inlinekeyboard_is_row(dic)
    
    keyboard.row(telebot.types.InlineKeyboardButton(text='<<', callback_data=f"{backCall}")) 
    return keyboard

def create_keyboard_question_from_sql(subjectID:int,backCall:str='project'):
    # idSubjectsOfDescription
    questions = sql.get_question_list_on(subjectID=subjectID)
    # points = sql.select_query('SubjectsOfDescription', f"subjectsType = '{forSubjectType}'")
    # sql.get_payload()
    dic = {}
    for question in questions:
        # dic[question['Question']] = f"question_{question['id']}"
        dic[question['nameButton']] = f"question_{question['id']}"
    keyboard = create_inlinekeyboard_is_row(dic)
    keyboard.row(telebot.types.InlineKeyboardButton(text='Онбординг', callback_data=f"onbording_{subjectID}")) 
    keyboard.row(telebot.types.InlineKeyboardButton(text='<<', callback_data=f"{backCall}")) 
    return keyboard