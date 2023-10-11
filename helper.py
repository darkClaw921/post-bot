
from loguru import logger
from datetime import datetime
from workRedis import *
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


if __name__ == '__main__':
    pass