import os
import ydb
import ydb.iam
from dotenv import load_dotenv
from helper import sum_dict_values, create_dict_questions
from pprint import pprint
from loguru import logger
#from helper import *
load_dotenv()

driver = ydb.Driver(
  endpoint=os.getenv('YDB_ENDPOINT'),
  database=os.getenv('YDB_DATABASE'),

  #credentials=ydb.iam.MetadataUrlCredentials(),)
  #credentials=ydb.AccessTokenCredentials(os.getenv('YDB_CREDINTALS_TOKEN')))
  credentials=ydb.iam.ServiceAccountCredentials.from_file(
           os.getenv("SA_KEY_FILE")
        ))
# Wait for the driver to become active for requests.G
driver.wait(fail_fast=True, timeout=5)
# Create the session pool instance to manage YDB sessions.
pool = ydb.SessionPool(driver)

def truncate_string(string, max_length):
    if len(string.encode('utf-8')) > max_length:
        return string[:max_length]
    else:
        return string
intList = ['all_token', 'all_messages', 'time_epoh', 'time_epoch','token',
           'orderID', 'stock_id','all_token','all_messages','user_id',
           'project_id','idProfile','idQuestionList','subjectID']

floatList = ['token_price','amount','price_open',
              'price_insert','price_close','bb_bu','all_price',
              'rate_change', 'lower_price', 'upper_price','need_price_close', 'price_now']

dateTimeList = ['date_time','date_close', 'need_data_close','date_open','date']
class Ydb:
    def replace_query(self, tableName: str, rows: dict):
        field_names = rows.keys()
        fields_format = ", ".join(field_names)
        my_list = list(rows.values())
    
        value = '('
        #for i in my_list:
        for key, value1 in rows.items():
            try:
                value1 = value1.replace('"',"'")    
            except:
                1 + 0
            
            #TODO переделать под разные форматы
            value1 = truncate_string(str(value1), 2000)            
            if key == 'id':
                value += f'{value1},'

            elif key in intList:
                value += f'{int(value1)},'
            
            elif key in floatList:
                value += f'{float(value1)},'
            
            elif key in dateTimeList:
                value += f'CAST("{value1}" AS datetime ),'
            else:
                value += f'"{value1}",'
            
        value = value[:-1] + ')'
        # values_placeholder_format = ', '.join(my_list)
        query = f"REPLACE INTO `{tableName}` ({fields_format}) VALUES {value}"
        print(query)
        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
            #session(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)


    def update_query(self, tableName: str, rows: dict, where: str):
        # 'where id > 20 '
        field_names = rows.keys()
        fields_format = ", ".join(field_names)
        my_list = list(rows.values())
        sets = ''
        for key, value in rows.items():
            if key in ['ID']:
                continue
            if key in floatList:
                sets += f'{key} = {float(value)},'
            elif key in intList:
                sets += f'{key} = {int(value)},'
            else:
                sets += f'{key} = "{value}",'

        sets = sets[:-1]

        # values_placeholder_format = ', '.join(my_list)
        query = f'UPDATE {tableName} SET {sets} WHERE {where}'
        # query = f"INSERT INTO {tableName} ({fields_format}) " \
        print(query)

        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)

    def plus_query_user(self, tableName: str, rows: dict, where: str):
        # 'where id > 20 '
        """складывает предыдущие значения row с новыми"""
        get = self.select_query(tableName, where)[0]
        row = 0
        try:
            get = {'all_price': float(get['all_price']), 'all_token': int(get['all_token']), 'all_messages':int(get['all_messages'])}
        except Exception as e:
            print('e', e)
            get = {'all_price': 0, 'all_token': 0, 'all_messages': 0}
        try:
            row = sum_dict_values(get, rows)
        except Exception as e:
            print('ошибка',e)
            row = rows
        print(f'{get=}') 
        print(f'{row=}') 
        self.update_query(tableName, row, where)

    def delete_query(self, tableName: str, where: str):
        # 'where id > 20 '
        query = f"DELETE FROM `{tableName}` WHERE {where}"
        #print(query)

        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)

    def create_table(self, tableName: str, fields: dict):
        # fields = {'id': 'Uint64', 'name': 'String', 'age': 'Uint64'}
        query = f"CREATE TABLE `{tableName}` ("
        for key, value in fields.items():
            query += f'{key} {value},'

        query = query[:-1] + ', PRIMARY KEY (id) ) '
        #print('CREATE TABLE',tableName)
        print(query)
        def a(session):
            session.execute_scheme(
                query,
                )
        return pool.retry_operation_sync(a)

    def insert_query(self, tableNameUserID: str, rows: dict):
        field_names = rows.keys()
        fields_format = ", ".join(field_names)
        my_list = list(rows.values())
    
        value = '('
        #for i in my_list:
        for key, value1 in rows.items():
            try:
                value1 = value1.replace('"',"'")    
            except:
                1 + 0
            
            #TODO переделать под разные форматы
            value1 = truncate_string(str(value1), 2000)            
            if key == 'id':
                value += f'{value1},'

            elif key in intList:
                value += f'{int(value1)},'
            
            elif key in floatList:
                value += f'{float(value1)},'
            elif key in dateTimeList:
                value += f'CAST("{value1}" AS datetime ),'


            else:
                value += f'"{value1}",'
            
        value = value[:-1] + ')'
        # values_placeholder_format = ', '.join(my_list)
        query = f"INSERT INTO `{tableNameUserID}` ({fields_format}) VALUES {value}"
        print(query)
        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
            #session(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)

    def get_context(self, tableNameUserID: str, whereModelDialog: str):
        query = f"""SELECT * FROM `{tableNameUserID}` where MODEL_DIALOG = "{whereModelDialog}" """
        #print(query)
        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        # string = b_string.decode('utf-8')
        # IndexError: list index out of range если нет данныйх
        #print('b',b)
        rez = b[0].rows
        #print('rez',rez)
        context = ''
        for i in rez:
            context += i['TEXT'].decode('utf-8')+ '\n'
        print('context',context)
        return context
   
    def get_payload(self, whereID: int, isBackPayload=False):
        if isBackPayload:
            query = f'SELECT back_payload FROM user WHERE id = {whereID}'
        else:
            query = f'SELECT payload FROM user WHERE id = {whereID}'
        print(query)

        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        # string = b_string.decode('utf-8')
        # IndexError: list index out of range если нет данныйх
        #print('b',b)
        if isBackPayload:
            rez = b[0].rows[0]['back_payload']
        else:
            rez = b[0].rows[0]['payload']
        #print('rez',rez)
        return rez
    
    def get_project_id(self, whereID: int):
        query = f'SELECT project_id FROM user WHERE id = {whereID}'
        print(query)
        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        rez = b[0].rows[0]['project_id']
        return rez
    
    def get_subject_id(self, whereID: int):
        query = f'SELECT subjectID FROM user WHERE id = {whereID}'
        print(query)
        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        rez = b[0].rows[0]['subjectID']
        return rez
    
    def get_call_back(self, whereID: int):
        query = f'SELECT call_back FROM user WHERE id = {whereID}'
        print(query)
        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        rez = b[0].rows[0]['call_back']
        return rez
    
    def get(self,what:str, whereID: int):
        query = f'SELECT {what} FROM user WHERE id = {whereID}'
        print(query)
        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        rez = b[0].rows[0][what]
        return rez
    
    def set_payload(self, userID: int, entity:str, isBackPayload=False):
        # if isBackPayload:
        # oldPayload=self.get_payload(userID)
        # query = f'UPDATE user SET back_payload = "{oldPayload}" WHERE id = {userID}' 
        # row ={
        #     'back_payload': oldPayload
        # }
        # self.update_query('user', row, where=f'id = {userID}')

        query = f"UPDATE user SET payload = '{entity}' WHERE id = {userID}"
        print(query)
        
         
        
        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)
    
    def set_project_id(self, userID: int, entity:int):
        query = f'UPDATE user SET project_id = {entity} WHERE id = {userID}'
        #print(query)
        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)
    
    def set_subject_id(self, userID: int, entity:int):
        query = f'UPDATE user SET subjectID = {entity} WHERE id = {userID}'
        #print(query)
        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)
    
    def set_call_back(self, userID: int, entity:int):
        query = f'UPDATE user SET call_back = "{entity}" WHERE id = {userID}'
        #print(query)
        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)
    
    def set(self, userID: int,what:str, entity:int):
        query = f'UPDATE user SET {what} = "{entity}" WHERE id = {userID}'
        #print(query)
        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)

    def get_currency_pair(self, whereID: int):
        query = f'SELECT currency_pair FROM order WHERE orderID = {whereID}'
        print(query)
        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        # string = b_string.decode('utf-8')
        # IndexError: list index out of range если нет данныйх
       
        #rez = b[0].rows[0].decode('utf-8')
        try:
            rez = b[0].rows[0]['currency_pair'].decode('utf-8')
        except:
            return 'нет в базе'
        print('rez',rez)
        return rez

    def select_query(self,tableName: str, where: str):
        # 'where id > 20 '
        query = f'SELECT * FROM {tableName} WHERE {where}'
        print(query)

        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        # string = b_string.decode('utf-8')
        # IndexError: list index out of range если нет данныйх
        #print('b',b)
        rez = b[0].rows
        #print('rez',rez)
        return rez
    
    def get_question_list_on(self,subjectID:int, onlyQuestion:bool=False):
        # 'where id > 20 '
        if onlyQuestion:
            query = f"SELECT * FROM QuestionList WHERE idSubjectsOfDescription = {subjectID} and typeQuestion in ('standart','generate')"
        else:
            query = f'SELECT * FROM QuestionList WHERE idSubjectsOfDescription = {subjectID}'
        print(query)

        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
       
        rez = b[0].rows
        #print('rez',rez)
        return rez
    
    def get_answer_on(self,questionID:int, forProfileID:int):
        # 'where id > 20 '
        query = f'SELECT * FROM ProfileDescription WHERE idQuestionList	= {questionID} and idProfile ={forProfileID}'
        print(query)

        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
       
        rez = b[0].rows
        #print('rez',rez)
        return rez
    
    def get_answer_list_on(self, subjectID:int, forProfileID:int, ):
        answers = []
        questions = self.get_question_list_on(subjectID=subjectID)
        # pprint(questions)
        for question in questions:
            # logger.critical(question)
            try:
                answer = self.get_answer_on(questionID=question['id'], forProfileID=forProfileID)[0]['Answer']
            except Exception as e:
                logger.debug("Нет ответа на этот вопрос",e)
                continue

            # answers.append(answer)
            answers.append({'tag':question['Tag'],
                             'answer':answer})
        return answers
    
    def get_all_answer_list(self, forProfileID:int, ):
        answers = []
        for subjectID in range(1,8):
            questions = self.get_question_list_on(subjectID=subjectID)
            # pprint(questions)
            for question in questions:
                # logger.critical(question)
                try:
                    answer = self.get_answer_on(questionID=question['id'], forProfileID=forProfileID)[0]['Answer']
                except Exception as e:
                    logger.debug("Нет ответа на этот вопрос",e)
                    continue

                # answers.append(answer)
                answers.append({'tag':question['Tag'],
                             'answer':answer})
        return answers 

    def plus_query_user(self, tableName: str, rows: dict, where: str):
        # 'where id > 20 '
        """складывает предыдущие значения row с новыми"""
        get = self.select_query(tableName, where)[0]
        row = 0
        try:
            get = {'all_price': float(get['all_price']), 'all_token': int(get['all_token']), 'all_messages':int(get['all_messages'])}
        except Exception as e:
            print('e', e)
            get = {'all_price': 0, 'all_token': 0, 'all_messages': 0}
        try:
            row = sum_dict_values(get, rows)
        except Exception as e:
            print('ошибка',e)
            row = rows
        print(f'{get=}') 
        print(f'{row=}') 
        self.update_query(tableName, row, where)

    def get_type_column(self):
        def a(session):
            # return session.DescribeTable.execute(
            #NOTE
            #  session = driver.table_client.session().create()
            result=  session.describe_table('/ru-central1/b1grd28shs5060j2itkp/etn3p0d1m9tqlqu38omt/user')
            print(f'{result=}')
            for column in result.columns:
                print("column, name:", column.name, ",", str(column.type.item).strip())
        b = pool.retry_operation_sync(a)
        # print(f'{b=}')
        return 0
        # b = pool.retry_operation_sync(a)

def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello World!',
    }

if __name__ == '__main__':
    sql = Ydb()
    a = sql.get_question_list_on(subjectID=1)
    # a = sql.get_answer_on(questionID=1, forProfileID=1696864099755)
    # a = sql.get_answer_list_on(subjectID=1, forProfileID=1697037106543)
    create_dict_questions(a)
    # pprint(a)
    pass
    # a = Ydb()
    #b = a.get_currency_pair(2)
    # row = {
    #     'time_epoh': 12,
    #     'amount': 1,
    #     'currency_pair' : "BTC_USDT",
    #     'date_open': 'now',
    #     'price_open': 2133,
    #     'status': 'open',
    #     'orderID': 3
    # }
    # b = a.insert_query('order',row)
    # print(b)