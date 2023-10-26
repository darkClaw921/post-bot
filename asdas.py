import datetime
from bitrix24 import Bitrix24
from pprint import pprint
# from ForWorkGSheet import Sheet
import math
import os
import pytz
from loguru import logger
# import workYDB

from dataclasses import dataclass

# sql = workYDB.Ydb()
tz = pytz.timezone('Europe/Moscow')

bit = Bitrix24('https://oto-hotels.bitrix24.ru/rest/254/vwrum1xi0a3feeck/')

@dataclass
class Deal:
    stage_vhod_bron: str = '0' # админы только в одной стадии заезд через 6 часов
    stage_projivanie_viezd: str = '17' # только админы
    stage_priem_kvartira:str = '7'

    stage_0_manager = ['NEW','UC_VDBF13','UC_17MKP2','UC_O6WWPN', 'UC_9QLBEE', 'UC_BZA6AD']
    stage_0_admin = ['UC_YJ58C3'] #заезд через 6 часов


timeReplaceAssigneg = 'UF_CRM_1688758617'
# кто на кого меняет
menagers = {1: 9,
            9: 1}

admins = {1: 9,
          9: 1}

week = {
    1: ['B', 'C', 'D', 'E', 'F', 'G', 'H'],
    2: ['J', 'K', 'L', 'M', 'N', 'O', 'P'],
    3: ['R', 'S', 'T', 'U', 'V', 'W', 'X'],
    4: ['Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF'],
    5: ['AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN'],
}

today = datetime.date.today()
SHEET_NAME = 'graphik - Oto Manager'
PATH_JSON_ACCAUNT = 'yandex-cloud-1-d54690faae5c.json'

def get_moscow_date():
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.datetime.now(moscow_tz)
    return moscow_time.strftime('%Y-%m')
#listName = 'Апрель'

# listName = get_moscow_date()
# sheet = Sheet(PATH_JSON_ACCAUNT, SHEET_NAME, listName)


def get_col_name():
    current_date = datetime.datetime.today()
    current_date_msk = current_date.astimezone(tz)
    print(f'{current_date_msk=}')
    today = current_date_msk.weekday()
    # print(today)  # 1
    today1 = current_date_msk.today().astimezone(tz)
    print(f'{today=}')
    print(f'{today1=}')
    week_number = get_week_of_day(today1)
    print('week_number: ', week_number)

    col = week[week_number][today]
    return col


def get_week_of_day(date):
    first_day = date.replace(day=1)
    iso_day_one = first_day.isocalendar()[1]
    iso_day_date = date.isocalendar()[1]
    adjusted_week = (iso_day_date - iso_day_one) + 1
    return adjusted_week


def get_assigned_graph_menedger():
    print('попали в получение менеджеров')
    col = get_col_name()
    maxMenegerStart = sheet.find_cell('Менеджеры').row + 5
    maxMenegerEnd = sheet.find_cell('Конец менеджеров').row 
    print(f'{maxMenegerStart=}')
    print(f'{maxMenegerEnd=}')
    users = []
    for i in range(maxMenegerStart, maxMenegerEnd):
        valueGraph = sheet.get_cell(row=f'{col}{i}')
        #print(f'{valueGraph=}')
        if valueGraph == 'TRUE':
            valueUsers = sheet.get_cell(row=f'A{i}')
            #print(f'{valueUsers=}')
            userID = valueUsers.split(' ')[0].replace('[', '').replace(']', '')
            users.append(int(userID))
    return users


def get_assigned_graph_admin():
    col = get_col_name()
    maxAdminStart = sheet.find_cell('Админы').row + 5
    maxAdminEnd =sheet.find_cell('Конец Админов').row
    allRows = maxAdminEnd - maxAdminStart
    users = []
    for i in range(maxAdminStart, maxAdminEnd):
        valueGraph = sheet.get_cell(row=f'{col}{i}')
        if valueGraph == 'TRUE':
            valueUsers = sheet.get_cell(row=f'A{i}')
            userID = valueUsers.split(' ')[0].replace('[', '').replace(']', '')
            users.append(int(userID))
    return users


def get_deals_meneger(users: list): #0
    col = get_col_name()
    print(f'попали в менеджеров {col} {users}')
    
    deals = bit.callMethod('crm.deal.list',
                            FILTER={'STAGE_SEMANTIC_ID': 'P',
                                    #'ASSIGNED_BY_ID': menagers[user],
                                    'CATEGORY_ID': 0,
                                    '!STAGE_ID': Deal.stage_0_admin,
                                    f'!{timeReplaceAssigneg}': today})
    
    try:
        count = math.ceil(len(deals) / len(users))
    except ZeroDivisionError:
        #print(f'{count=}')
        print(f'делить на 0')
        return 0 

    countUpdate = 0
    #print(f'{deals=}')
    indexUser = 0
    print(f'{len(deals)=}')
    print(f'{count=}')
    
    for deal in deals:
       # print(deal['CONTACT_ID'])
        #print(deal['ID'])
        try:
            bit.callMethod('crm.contact.update', ID=deal['CONTACT_ID'], fields={
                'ASSIGNED_BY_ID': str(users[indexUser]),
                #'UF_CRM_1680207208770': today,
            })
        except:
            continue
        bit.callMethod('crm.deal.update', ID=deal['ID'], fields={
                'ASSIGNED_BY_ID': str(users[indexUser]),
                '!{timeReplaceAssigneg}': today,})
            #print(f'обновили {deal["ID"]} для {user}')
        countUpdate +=1
        if countUpdate >= count:
            print(f'{countUpdate=}')
            print(f'добавили пользователю {users[indexUser]} : {countUpdate} сделок')
            indexUser += 1
            countUpdate = 0
    try:
        print(f'сделки кончились добавили пользователю {users[indexUser]} : {countUpdate} сделок')
    except IndexError: 
        print(f'сделки кончились добавили пользователю {users[indexUser-1]} : {countUpdate} сделок')

def get_deals_meneger7(users: list): #0
    col = get_col_name()
    print(f'попали в менеджеров {col} {users}')
    
    deals = bit.callMethod('crm.deal.list',
                            FILTER={'STAGE_SEMANTIC_ID': 'P',
                                    #'ASSIGNED_BY_ID': menagers[user],
                                    'CATEGORY_ID': Deal.stage_priem_kvartira,
                                    #'!STAGE_ID': Deal. , })
                                    f'!{timeReplaceAssigneg}': today})
    
    try:
        count = math.ceil(len(deals) / len(users))
    except ZeroDivisionError:
        #print(f'{count=}')
        print(f'делить на 0')
        return 0 

    countUpdate = 0
    #print(f'{deals=}')
    indexUser = 0
    print(f'{len(deals)=}')
    print(f'{count=}')
    
    for deal in deals:
       # print(deal['CONTACT_ID'])
        #print(deal['ID'])
        try:
            bit.callMethod('crm.contact.update', ID=deal['CONTACT_ID'], fields={
                'ASSIGNED_BY_ID': str(users[indexUser]),
                #'UF_CRM_1680207208770': today,
            })
        except:
            continue
        bit.callMethod('crm.deal.update', ID=deal['ID'], fields={
                'ASSIGNED_BY_ID': str(users[indexUser]),
                '!{timeReplaceAssigneg}': today,})
            #print(f'обновили {deal["ID"]} для {user}')
        countUpdate +=1
        if countUpdate >= count:
            print(f'{countUpdate=}')
            print(f'добавили пользователю {users[indexUser]} : {countUpdate} сделок')
            indexUser += 1
            countUpdate = 0
    try:
        print(f'сделки кончились добавили пользователю {users[indexUser]} : {countUpdate} сделок')
    except IndexError: 
        print(f'сделки кончились добавили пользователю {users[indexUser-1]} : {countUpdate} сделок')

def get_deals_admin(users: list): #0
    col = get_col_name()
    print(f'попали в менеджеров {col} {users}')
    
    deals = bit.callMethod('crm.deal.list',
                            FILTER={'STAGE_SEMANTIC_ID': 'P',
                                    #'ASSIGNED_BY_ID': menagers[user],
                                    'CATEGORY_ID': 0,
                                    'STAGE_ID': Deal.stage_0_admin ,
                                    f'!{timeReplaceAssigneg}': today})
    
    try:
        count = math.ceil(len(deals) / len(users))
    except ZeroDivisionError:
        #print(f'{count=}')
        print(f'делить на 0')
        return 0 

    countUpdate = 0
    #print(f'{deals=}')
    indexUser = 0
    print(f'{len(deals)=}')
    print(f'{count=}')
    
    for deal in deals:
       # print(deal['CONTACT_ID'])
        #print(deal['ID'])
        try:
            bit.callMethod('crm.contact.update', ID=deal['CONTACT_ID'], fields={
                'ASSIGNED_BY_ID': str(users[indexUser]),
                #'UF_CRM_1680207208770': today,
            })
        except:
            continue
        bit.callMethod('crm.deal.update', ID=deal['ID'], fields={
                'ASSIGNED_BY_ID': str(users[indexUser]),
                '!{timeReplaceAssigneg}': today,})
            #print(f'обновили {deal["ID"]} для {user}')
        countUpdate +=1
        if countUpdate >= count:
            print(f'{countUpdate=}')
            print(f'добавили пользователю {users[indexUser]} : {countUpdate} сделок')
            indexUser += 1
            countUpdate = 0
    try:
        print(f'сделки кончились добавили пользователю {users[indexUser]} : {countUpdate} сделок')
    except IndexError: 
        print(f'сделки кончились добавили пользователю {users[indexUser-1]} : {countUpdate} сделок')
            

def get_deals_admin_cate17(users: list):
    col = get_col_name()
    print(f'попали в admin_Cat17 {col} {users}')
    #count = math.ceil(len(deals) / len(users))
    deals = bit.callMethod('crm.deal.list',
                            FILTER={'STAGE_SEMANTIC_ID': 'P',
                                    #'ASSIGNED_BY_ID': menagers[user],
                                    'CATEGORY_ID': Deal.stage_projivanie_viezd,
                                    # '!STAGE_ID': 'что-то', })
                                    f'!{timeReplaceAssigneg}': today})
    
    try:
        count = math.ceil(len(deals) / len(users))
    except ZeroDivisionError:
        #print(f'{count=}')
        print(f'делить на 0')
        return 0 
    countUpdate = 0
    #print(f'{deals=}')
    indexUser = 0
    print(f'{len(deals)=}')
    print(f'{count=}')

    for deal in deals:
        try:
            bit.callMethod('crm.contact.update', ID=deal['CONTACT_ID'], fields={
                'ASSIGNED_BY_ID': str(users[indexUser]),
                #'UF_CRM_1680207208770': today,
            })
        except:
            continue
        bit.callMethod('crm.deal.update', ID=deal['ID'], fields={
                'ASSIGNED_BY_ID': str(users[indexUser]),
                f'{timeReplaceAssigneg}': today,})
            #print(f'обновили {deal["ID"]} для {user}')
        countUpdate +=1
        if countUpdate >= count:
            print(f'{countUpdate=}')
            print(f'добавили пользователю {users[indexUser]} : {countUpdate} сделок')
            indexUser += 1
            countUpdate = 0
    try:
        print(f'сделки кончились добавили пользователю {users[indexUser]} : {countUpdate} сделок')
    except IndexError: 
        print(f'сделки кончились добавили пользователю {users[indexUser-1]} : {countUpdate} сделок')

@logger.catch
def get_users():
    prepareUser = []
    users = bit.callMethod('user.get', FILTER ={'ACTIVE':True})
    pprint(users)
    for user in users:
        user_id = user["ID"]
        try:
            user_name = user["NAME"]
        except:
            user_name = f'NO NAME {user_id}'

        prepareUser.append(f'[{user_id}] {user_name}')
    return prepareUser

def update_user():
    users = get_users()
    listName = 'users'
    sheetUser = Sheet(PATH_JSON_ACCAUNT, SHEET_NAME, listName)
    for i, user in enumerate(users):
        sheetUser.send_cell(f'G{i+2}', user)
    

def main():
    col = get_col_name()
    #update_user()
    usersMenedger = get_assigned_graph_menedger()
    print(f'{usersMenedger=}')
    get_deals_meneger(usersMenedger)
    get_deals_meneger7(usersMenedger)

    userAdmins = get_assigned_graph_admin()
    print(f'{userAdmins=}')
    get_deals_admin(userAdmins)
    get_deals_admin_cate17(userAdmins)
    
    table = {'id':1,
            'menedger':usersMenedger,
            'adminCat3':userAdmins,
            'adminCat5':userAdmins,}
    sql.replace_query('my_table', table)

def handler(event, context):
    #get_assigned_graph_menedger()
    
    
    # main()
    update_user()
    
    
    #maxUser = sheet.find_cell('Админы').row - 3
    #print(f'{maxUser=}')
    return {
        'statusCode': 200,
        'body': 'Успешно',
    }
update_user()
