import redis
import json
r = redis.Redis(host='localhost', port=6379, decode_responses=False)

def add_message_to_history(userID:str, role:str, message:str):
    mess = {'role': role, 'content': message}
    r.lpush(userID, json.dumps(mess))

def add_long_message(userID:str, tag:str, message:str):
    mess = {'text': message, 'tag': tag}
    r.lpush(userID+'_long', json.dumps(mess))

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

def get_long_message(userID:str):
    items = r.lrange(userID+'_long', 0, -1)
    history = [json.loads(m.decode("utf-8")) for m in items[::-1]]
    return history[0]['text']

def clear_history(userID:str):
    r.delete(userID)