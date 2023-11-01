import redis
import json
r = redis.Redis(host='localhost', port=6379, decode_responses=False)
#TODO добавить удаление длинного сообщения
def add_message_to_history(userID:str, role:str, message:str):
    mess = {'role': role, 'content': message}
    r.lpush(userID, json.dumps(mess))

def add_long_message(userID:int, allMessage:dict):
    """_summary_

    Args:
        userID (str): 
        allMessage (dict): {tag: text}
    """
    clear_long_message(userID)
    # mess = {'text': message, 'tag': tag}
    r.lpush(str(userID)+'_long', json.dumps(allMessage))

def add_old_history(userID:str, history:list):
    his = history.copy()
    clear_history(userID)
    for i in his:
        mess = i
        r.lpush(userID, json.dumps(mess))

def get_history(userID:str):
    items = r.lrange(userID, 0, -1)
    history = [json.loads(m.decode("utf-8")) for m in items[::-1]]
    return history

def get_long_message(userID:int):
    items = r.lrange(str(userID)+'_long', 0, -1)
    history = [json.loads(m.decode("utf-8")) for m in items[::-1]]
    return history

def clear_long_message(userID:int):
    r.delete(str(userID)+'_long')

def clear_history(userID:str):
    r.delete(userID)

if __name__ == '__main__':
    a = get_long_message(308789390)
    print(a)