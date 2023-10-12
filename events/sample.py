
from pymongo import MongoClient

def get_db_handle(db_name,host,port,**cred):
    client = MongoClient(host=host,port=int(port),**cred)
    db_handle = client[db_name]
    return db_handle

# user_db = get_db_handle('user','localhost',27017)
# d = user_db.credentials.find_one()


def update_dict(old_data,new_data):
    print(old_data, new_data)
    c = []
    for k in set(old_data) & set(new_data):
        if isinstance(old_data[k],bool):
            c.append((k,new_data[k]))
            continue
        if isinstance(old_data[k],str):
            if isinstance(new_data[k],list):
                c.append((k,[old_data[k]] + new_data[k]))
            else:
                c.append((k,[old_data[k] , new_data[k]]))
            continue
        if isinstance(old_data[k],list):
            if isinstance(new_data[k],list):
                c.append((k,old_data[k] + new_data[k]))
            else:
                c.append((k,old_data[k] + [new_data[k]]))
            continue
        else:
            c.append((k,old_data[k] + new_data[k]))
        
    updated_dict = dict([(k,v) for k,v in old_data.items()] + [(k,v) for k,v in new_data.items()]+c)
    return updated_dict

o = {
    'name':'durgai',
    'status':True,
    'msg':['m1'],
    'msg_str':'m1',
    'msg_arr':['m1']
}
n = {
    'name':'raj',
    'status':False,
    'msg':['m2'],
    'msg_str':['m2'],
    'msg_arr':'m2'
}
print(update_dict(o,n))