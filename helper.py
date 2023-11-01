
from loguru import logger
from datetime import datetime
from workRedis import *
import time
from dataclasses import dataclass
from pprint import pprint
from promtTXT import target
import speech_recognition as sr
language='ru_RU'
r = sr.Recognizer()


@dataclass
class SubjectType:
    class Profile_info:
        class Target:
            lastIDquestions = 6

        class Product:
           lastIDquestions = 10
        class Tov:
           lastIDquestions = 16

        type = 'profileInfo'
        id = 1
    # profileInfoStr = 'profileInfo'


# any
def time_epoch():
    from time import mktime
    dt = datetime.now()
    sec_since_epoch = mktime(dt.timetuple()) + dt.microsecond/1000000.0

    millis_since_epoch = sec_since_epoch * 1000
    return int(millis_since_epoch)

def remove_empty_lines(text):
    lines = text.splitlines()  # Разделение текста на отдельные строки
    stripped_lines = (line.strip() for line in lines)  # Удаление начальных и конечных пробелов
    non_empty_lines = (line for line in stripped_lines if line)  # Отбор только непустых строк
    return "\n".join(non_empty_lines) 

def timestamp_to_date(timestap, pattern = '%Y-%m-%dT%H:%M:%SZ'):
   
    """timestamp

    Returns:
        str: %Y-%m-%dT%H:%M:%SZ
    """
    a = time.gmtime(timestap)
    date_time = datetime(*a[:6])
    date_string = date_time.strftime(pattern)
    
    return date_string

def sum_dict_values(dict1, dict2):
    result = {}

    for key in dict1:
        if key in dict2:
            result[key] = dict1[key] + dict2[key]
        else:
            result[key] = dict1[key]

    for key in dict2:
        if key not in dict1:
            result[key] = dict2[key]

    return result

def split_string_by_length(input_string, length):
    return [input_string[i:i + length] for i in range(0, len(input_string), length)]

#telegram 
def summary(userID, error, isDEBUG):
    if isDEBUG : bot.send_message(userID, error)
        #bot.send_message(userID, 'начинаю sammury: ответ может занять больше времени, но не более 3х минут')
    history = get_history(str(userID))
    summaryHistory = gpt.summarize_questions(history)
    logger.info(f'summary истории {summaryHistory}')

    history = [summaryHistory]
    history.extend([{'role':'user', 'content': text}])
    add_old_history(userID,history)
    history = get_history(str(userID))
    logger.info(f'история после summary {history}')
    
    answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, text, history, model_index,temp=0.5, verbose=0)
    bot.send_message(message.chat.id, answer)
    add_message_to_history(userID, 'assistant', answer)

def recognise(filename):
    with sr.AudioFile(filename) as source:
        audio_text = r.listen(source)
        try:
            text = r.recognize_google(audio_text,language=language)
            print('Converting audio transcripts into text ...')
            print(text)
            return text
        except:
            print('Sorry.. run again...')
            return "Sorry.. run again..."

def find_key_words(text):

    import re
    # text = "Текст со значениями [1], [2441], [asdfasf]= и [4]"

    pattern = r'\[.*?\]'  # регулярное выражение для поиска значений в формате [*]

    values = re.findall(pattern, text)
    # print(values)
    return values

def find_text_from_promt(forSubjectType, text):
    startText = "{"+forSubjectType+"}"
    endText = "{"+forSubjectType+"}"
    start_index = text.find(str(startText))
    end_index = text.rfind(str(endText))
 
    if start_index != -1 and end_index != -1:  # Если найдены оба индекса
        start_index += len(startText)
        result = text[start_index:end_index].strip()  # Извлекаем текст между {profileInfo}
        # print(result)
        return result
    else:
        print("Не найдено")

def create_dict_questions(questions:list)->dict:
    dic = {}
    for i, quest in enumerate(questions):
        dic[i+1]={'tag': quest['Tag'],
                'text': quest['Question'],
                'id': quest['id']}
    pprint(dic)
    return dic


if __name__ == '__main__':
    text = target
    # sybjectType = '{profileInfo}'
    # sybjectType = 'profileInfo'
    # find_text_from_promt(forSubjectType=sybjectType, text=text)
    a = find_key_words(text)
    print(a)
    pass