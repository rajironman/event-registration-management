import bcrypt
from pymongo import MongoClient
import random

# function to get the mongodb database handler
mongoClient = None
def get_db_handle(db_name,host='localhost',port=27017,**cred):
    global mongoClient
    if not mongoClient:
        try:
            mongoClient = MongoClient(host=host,port=int(port),**cred)
        except Exception as e:
            print(e)
    db_handle = mongoClient[db_name]
    return db_handle


def create_account(username,password):
    data = {}
    data['msg'] = []
    user_db = get_db_handle('user')

    hash = bcrypt.hashpw(password.encode(),bcrypt.gensalt())

    credentials = user_db.credentials.find_one(filter={'username':username})
    if credentials:
        data['msg'].append('user name already exists')
        data['return_code'] = False
        return data


    try:
        user_db.credentials.insert_one({'username':username,'hash':hash})
        data['msg'].append('account created')
        data['return_code'] = True
    except:
        pass
    finally:
        return data

def login(username,password):
    data = {}
    data['msg'] = []
    user_db = get_db_handle('user','localhost',27017)
    credentials = user_db.credentials.find_one(filter={'username':username})
    if not credentials:
        data['msg'].append('user name does not exists')
        data['return_code'] = False
        return data

    if bcrypt.checkpw(password.encode(),credentials['hash']):
        data['return_code'] = True
        data['msg'].append('logged in successfully')

        import string
        #  generating auth key
        auth_key = "".join(random.choices(string.ascii_letters + string.digits,k=12))
        user_db.credentials.update_one({'username':username},{'$set':{'auth_key':auth_key}})
        data['username'] = username
        data['auth_key'] = auth_key

    else:
        data['msg'].append('failed to match password...')
        data['return_code'] = False
    return data

def authenticate(auth_token):
    user_db = get_db_handle('user','localhost',27017)
    credential = user_db.credentials.find_one(filter={'username':auth_token['username']})
    if credential and 'auth_key' in credential and 'username' in credential:
        if(str(credential['auth_key']) == str(auth_token['auth_key'])):
            return True
    return False