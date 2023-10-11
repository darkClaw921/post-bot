from datetime import date
import ydb
import ydb.iam
import os
from dotenv import load_dotenv
load_dotenv()

class Employee:
    # driver = ydb.Driver(
    #     endpoint=os.getenv('YDB_ENDPOINT'),
    #     database=os.getenv('YDB_DATABASE'),

    #     #credentials=ydb.iam.MetadataUrlCredentials(),)
    #     #credentials=ydb.AccessTokenCredentials(os.getenv('YDB_CREDINTALS_TOKEN')))
    #     credentials=ydb.iam.ServiceAccountCredentials.from_file(
    #             os.getenv("SA_KEY_FILE")))
    
    def __init__(self, name, birth_date):
        self.name = name
        self.birth_date = birth_date
    def __get__(self, obj, cls):
        print("Trying to access from {0} class {1}".format(obj, cls))
    
    def __getattr__(self, attr):
        print("Yep, I know", attr)
    
    
    def print_name(self):
        print('name')

    @property
    def name(self):
        return self._name

    @property
    def birth_date(self):
        return self._birth_date
    
    @name.setter
    def name(self, value):
        self._name = value.upper()

    @birth_date.setter
    def birth_date(self, value):
        self._birth_date = date.fromisoformat(value)

    def __getattribute__(self, name):
        # if name.endswith("_please"):
        # return object.__getattribute__(self, name.replace("_please", ""))
        
        a = object.__getattribute__(self, name)
        print(a)
        a.print_name()
        # raise AttributeError("And the magic word!?")
    
    # def __setattr__(self, name, value):
    #     print("Yep, I know", name, value)


if __name__ =='__main__':
    john = Employee("John", "2001-02-07")
    john.name = '12'
    john.namesd = 12
    a = john.namesd.name=54
    print(a)