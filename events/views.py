from django.http import JsonResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import json
from pymongo import MongoClient
from bson.json_util import dumps,loads
from bson.objectid import ObjectId
from django.http import FileResponse
from authentication import auth
import os

# function to get the mongodb database handler
mongoClient = None
def get_db_handle(db_name):
    global mongoClient
    if not mongoClient:
        try:
            mongo_url = "mongodb+srv://rajironman:14vde7DS680gsQP8@erm.tbrmcs5.mongodb.net/?retryWrites=true&w=majority"
            mongoClient = MongoClient(mongo_url)
        except Exception as e:
            print(e)
    db_handle = mongoClient[db_name]
    return db_handle



# to merge to dictionary without loss of data for duplicate keys  
def update_dict(old_data,new_data):
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


# serving the static & uploaded files
def file(request,filename):
    print(filename)
    if not os.path.isfile('media/'+filename):
        raise Http404
    return FileResponse(open('media/'+filename,'rb'))

@csrf_exempt
def index(request):
    return file(request,'static/index.html')

@csrf_exempt
def events(request):
    msg = [] 
    events_db = get_db_handle('events_db')
    next_exists = 0
    prev_exists = 0
    next_dir = "$lt"
    prev_dir = "$gt"
    event_data = 0
    cursor = "ev_id"
    username_filter = {}
    limit = int(request.POST['limit']) if ( 'limit' in request.POST ) else 4
    limit = min(limit,24)
    limit = max(limit,2)
    print(limit)

    exclusion_dict = {"username":0,"_id":0}
    if 'username' in request.POST and 'auth_key' in request.POST:
        if auth.authenticate({'username':request.POST['username'],"auth_key":request.POST['auth_key']}):
            username_filter = {"username":request.POST['username']}


    if request.POST and 'dir' in request.POST:
            dir = (request.POST['dir']) if ( 'dir' in request.POST ) else 'next'
            dir = next_dir if dir == "next" else prev_dir
            cursor_value = int(request.POST['cursor_value'])
            sort_value = -1 if dir == "$lt" else 1
            try:
                event_data = list(events_db.event_data_collection.find({cursor:{dir:cursor_value},**username_filter},exclusion_dict).sort(cursor,sort_value).limit(int(limit)))
            except Exception as e:
                # for_dev_only
                msg.append(str(e))
                print(e)

    if event_data == 0:
        event_data = list(events_db.event_data_collection.find({**username_filter},exclusion_dict).sort(cursor,-1).limit(limit))

    # sorting event_data so as to make pagination better by selecting max_id and min_id
    event_data.sort(key=lambda event: event[cursor],reverse=True)

    if len(event_data):
        max_id = int(event_data[0][cursor])
        min_id = int(event_data[-1][cursor])

        next_exists = events_db.event_data_collection.count_documents({cursor:{next_dir:min_id}},limit=1)
        prev_exists = events_db.event_data_collection.count_documents({cursor:{prev_dir:max_id}},limit=1)

        meta_data = {'next_exists':next_exists,'prev_exists':prev_exists,'min_id':min_id,'max_id':max_id}
    else:
        meta_data = {}
    
    count = len(event_data)
    msg.append('count:'+str(count))

    return JsonResponse({'events':dumps(event_data),'meta_data':meta_data,'msg':msg})

@csrf_exempt
def event(request,ev_id):
    # authetication
    authenticated = False
    if 'username' in request.POST and 'auth_key' in request.POST:
        auth_token = {'username':request.POST['username'],'auth_key':request.POST['auth_key']}
        if auth.authenticate(auth_token):
            authenticated = True
    
    events_db = get_db_handle('events_db')
    event = events_db.event_data_collection.find_one({"ev_id":int(ev_id)})

    registered = False
    collection_name = get_collection_name_for_event(ev_id)
    if events_db[collection_name].find_one({"username":request.POST['username']}):
        registered = True

    return JsonResponse({'event_data':dumps(event),'registered':registered})

@csrf_exempt
def unregister(request):
    if not ( 'ev_id' in request.POST and 'username' in request.POST and 'auth_key' in request.POST ):
        return JsonResponse({'msg':['invalid request'],'return_code':0})
    
    auth_token = {'username':request.POST['username'],'auth_key':request.POST['auth_key']}
    if not auth.authenticate(auth_token):
        return JsonResponse({'msg':['authentication failed.Try to login again.'],"error_msg":"AUTH_FAILED",'return_code':0})

    ev_id = request.POST['ev_id']

    events_db = get_db_handle('events_db')
    collection_name = get_collection_name_for_event(ev_id)
    try:
        if (events_db[collection_name].delete_many({"username":request.POST['username']})).deleted_count > 0:
            return JsonResponse({'msg':['unregistered successfully'],'return_code':1})
    except Exception as e:
        print(e)
    return JsonResponse({'msg':['Try again'],'return_code':0})

@csrf_exempt
def create_event(request):
    events_db = get_db_handle('events_db')
    data = {}
    msg = data['msg'] = []
    data['return_code'] = 0


    # authetication
    if 'username' in request.POST and 'auth_key' in request.POST:
        auth_token = {'username':request.POST['username'],'auth_key':request.POST['auth_key']}
        if not auth.authenticate(auth_token):
            print((auth_token))
            msg.append('authentication failed.Try to login again.')
            return JsonResponse(data)
    else:
        msg.append('login first')
        return JsonResponse(data)

    #checking whether the image file is 
    if not 'ev_poster' in request.FILES:
        msg.append('poster image is missing')
        return JsonResponse(data)

    # arranging the event data
    event_data = {}
    event_data_keys = [('ev_title','title'),('ev_date','date'),('ev_reg_date','registration closing date'),('ev_host_name','host name'),('ev_desc','description'),('ev_location','location')]
    for key,key_text in event_data_keys:
        if request.POST[key]:
            event_data[key] = request.POST[key]
        else:
            msg.append(f'field : {key_text} is missing')
            return JsonResponse(data)

    title_and_date = {'username':request.POST['username'],'ev_title':event_data['ev_title'],'ev_date':event_data['ev_date']}
    old_event = events_db.event_data_collection.find_one(title_and_date,{"_id":0,"username":0})
    if old_event:
        msg.append('You have already created a event with the same title on the same date')
        return JsonResponse(data)

    #including the username of the event host
    event_data['username'] = request.POST['username']

    # arranging the required details
    ev_req_det_json = json.loads(request.POST['ev_req_det'])
    ev_req_det_dict = {'name':'text'}
    for key,value in ev_req_det_json.items():
        if isinstance(key,str) and (isinstance(value,str) or isinstance(value,list)):
            ev_req_det_dict[key] = value
        else:
            msg.append(f'{key} , {value} at required details are not in correct format')
            return JsonResponse(data)
    
    # adding the required details in event data
    event_data['ev_req_det'] = ev_req_det_dict


    ev_id = 1
    collection_name = 'event_data_collection'
    # to check whether this reg_id already exists in event_data_colllection
    loop_counter = 0
    while events_db[collection_name].find_one({"ev_id":ev_id}) and loop_counter < 3:
        print('loop counter:',loop_counter)
        max_id_record = list(events_db[collection_name].find().sort("ev_id",-1).limit(1))
        if len(max_id_record) == 0:
            break
        ev_id = int(max_id_record[0]['ev_id']) + 1
        
        # for controling the number of loop
        loop_counter += 1



    # including the unique id in event data
    event_data['ev_id'] = int(ev_id)

    # verify the image
    from PIL import Image
    try:
        print(Image.open(request.FILES['ev_poster']).verify())
    except Exception as e:
        print(e)
        msg.append('Invalid image, Try selecting other image')
        return JsonResponse(data)


    # insert the record  in event details
    try:
        event_object_id = events_db.event_data_collection.insert_one(event_data).inserted_id
    except Exception as e:
        msg.append('Error, Try again')
        return JsonResponse(data)

    
    # saving the file
    poster_img_file = request.FILES['ev_poster']
    file_ext = poster_img_file.name.split('.')[-1]
    new_filename = "upload/img" + '.' + file_ext
    fs = FileSystemStorage()
    actual_new_filename = fs.save(new_filename,poster_img_file)


    # updating the poster image path
    update_result = events_db.event_data_collection.update_one({'_id':event_object_id},{'$set':{'ev_poster_path':actual_new_filename}})
    if update_result.modified_count:
        msg.append('successfully created event')
        return JsonResponse(data)
    msg.append('Please, Try again.')
    return JsonResponse(data)


@csrf_exempt
def delete_event(request):
    events_db = get_db_handle('events_db')

    # authetication
    if 'username' in request.POST and 'auth_key' in request.POST:
        auth_token = {'username':request.POST['username'],'auth_key':request.POST['auth_key']}
        if not auth.authenticate(auth_token):
            return JsonResponse({'msg':['authentication failed.Try to login again.'],"error_msg":"AUTH_FAILED",'return_code':0})
    else:
        return JsonResponse({'msg':['login first'],'return_code':0})

    username = request.POST['username']
    ev_id = int(request.POST['ev_id'])
    event_data = events_db.event_data_collection.find_one({"username":username,"ev_id":ev_id})
    delete_result = events_db.event_data_collection.delete_one({"username":username,"ev_id":ev_id})
    if delete_result.deleted_count:
        collection_name = get_collection_name_for_event(ev_id)
        events_db.drop_collection(collection_name)
        if 'ev_poster_path' in event_data:
            ev_poster_path = 'media/'+event_data['ev_poster_path']
            if os.path.isfile(ev_poster_path):
                os.remove(ev_poster_path)
            else:
                return JsonResponse({'msg':['deleted successfully',ev_poster_path+'image file not found'],'return_code':1})

        return JsonResponse({'msg':['deleted successfully'],'return_code':1})
    return JsonResponse({'msg':['invalid request'],'return_code':0})


def get_collection_name_for_event(ev_id):
    return 'event_' + str(ev_id) + "_collection"


@csrf_exempt
def register_in_event(request):
    events_db = get_db_handle('events_db')

    # authetication
    if 'username' in request.POST and 'auth_key' in request.POST:
        auth_token = {'username':request.POST['username'],'auth_key':request.POST['auth_key']}
        if not auth.authenticate(auth_token):
            return JsonResponse({'msg':['authentication failed.Try to login again.'],"error_msg":"AUTH_FAILED",'return_code':0})
    else:
        return JsonResponse({'msg':['login first'],'return_code':0})
    
    if 'required_details' in request.POST and request.POST['required_details'] and request.POST['ev_id']:
        required_details = json.loads(request.POST['required_details'])
        collection_name = get_collection_name_for_event(request.POST['ev_id'])


        reg_id = 1
        # to check whether this reg_id already exists in event_data_colllection
        loop_counter = 0
        while events_db[collection_name].find_one({"reg_id":reg_id}) and loop_counter < 3:
            print('loop counter:',loop_counter)
            max_id_record = list(events_db[collection_name].find().sort("reg_id",-1).limit(1))

            if len(max_id_record) == 0:
                break
            reg_id = int(max_id_record[0]['reg_id']) + 1
            
            # for controling the number of loop
            loop_counter += 1

        required_details_arranged = {}
        required_details_arranged['reg_id'] = reg_id
        required_details_arranged['username'] = request.POST['username']
        required_details_arranged = {**required_details_arranged,**required_details}

        if events_db[collection_name].find_one({'username':request.POST['username']}):
            print(events_db[collection_name].find_one({'username':request.POST['username']}))
            return JsonResponse({'msg':['Already registered'],'return_code':0})
        
        if events_db[collection_name].insert_one(required_details_arranged):
            return JsonResponse({'msg':['registered successfully'],'return_code':1})
        
    return JsonResponse({'msg':['Try again'],'return_code':0})


@csrf_exempt
def get_participants_details(request):
    from pandas import DataFrame
    events_db = get_db_handle('events_db')

    # authetication
    if 'username' in request.POST and 'auth_key' in request.POST:
        auth_token = {'username':request.POST['username'],'auth_key':request.POST['auth_key']}
        if not auth.authenticate(auth_token):
            return JsonResponse({'msg':['authentication failed.Try to login again.'],"error_msg":"AUTH_FAILED",'return_code':0})
    else:
        return JsonResponse({'msg':['login first'],'return_code':0})
    
    if ( not 'ev_id' in request.POST ) or ( not request.POST['ev_id']):
        return JsonResponse({'msg':['invalid request'],'return_code':0})
    
    
    ev_id = int(request.POST['ev_id'])
    collection_name = get_collection_name_for_event(ev_id)

    if not events_db.event_data_collection.find_one({"ev_id":ev_id,"username":request.POST['username']}):
        print(events_db.event_data_collection.find_one({"ev_id":ev_id}))
        return JsonResponse({'msg':['invalid request...'],'return_code':0})

    participants_details = list(events_db[collection_name].find({},{"_id":0}))
    registered_participants_details_json = json.dumps(participants_details)
    print(registered_participants_details_json)

    directory = 'media/participants_details/'
    if not os.path.isdir(directory):
        os.mkdir(directory)
    csv_file_name = collection_name+'.csv'
    df = DataFrame(participants_details)
    df.to_csv(directory+csv_file_name)
    return JsonResponse({'participants_details':participants_details,'file_name':csv_file_name,'return_code':1})


@csrf_exempt
def get_participants_details_csv(request):

    # authetication
    if 'username' in request.POST and 'auth_key' in request.POST:
        auth_token = {'username':request.POST['username'],'auth_key':request.POST['auth_key']}
        if not auth.authenticate(auth_token):
            return JsonResponse({'msg':['authentication failed.Try to login again.'],"error_msg":"AUTH_FAILED",'return_code':0})
    else:
        return JsonResponse({'msg':['login first'],'return_code':0})
    
    filename = 'participants_details/' + request.POST['file_name']
    if not os.path.isfile('media/'+filename):
        raise Http404
    return FileResponse(open('media/'+filename,'rb'))

@csrf_exempt
def feedback(request):
    if not( 'name' in request.POST and len(request.POST['name']) and 'feedback' in request.POST and len(request.POST['feedback'])):
        return JsonResponse({'msg':['Name and feedback are required.'],'return_code':0})
    feedbacks_db = get_db_handle('feedbacks_db')
    if feedbacks_db.feedback_collection.find_one({'name':request.POST['name'],'feedback':request.POST['feedback']}):
        return JsonResponse({'msg':['This feedback with same message and same name already exists.So try again with different feedback message'],'return_code':0})
    inserted_id = feedbacks_db.feedback_collection.insert_one({'name':request.POST['name'],'feedback':request.POST['feedback']}).inserted_id
    if inserted_id:
        return JsonResponse({'msg':['feedback submitted successfully'],'return_code':1})
    return JsonResponse({'msg':['Try again'],'return_code':0})

@csrf_exempt
def get_feedbacks(request):
    feedbacks_db = get_db_handle('feedbacks_db')
    feedbacks = list(feedbacks_db.feedback_collection.find({},{"_id":0}).sort("_id",-1).limit(30))
    return JsonResponse({'feedbacks':feedbacks})