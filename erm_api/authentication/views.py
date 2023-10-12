from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from . import auth

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


@csrf_exempt
def create_account(request):
    if request.method == "POST":
        data = {}
        data['msg'] = []
        username = request.POST.get('username')
        password = request.POST.get('password')


        if not username:
            data['msg'].append('empty username')
            return JsonResponse(data)

        new_data = auth.create_account(username,password)
        data = update_dict(data,new_data)

        if 'return_code' in new_data and new_data['return_code']:
            new_data = auth.login(username,password)
            data = update_dict(data,new_data)

        return JsonResponse(data)

@csrf_exempt
def login(request):
    if request.method == "POST":
        data = {}
        data['msg'] = []

        username = request.POST.get('username')
        password = request.POST.get('password')

        print(request.POST.values)
        if(not (username and password)):
            data['msg'].append('username and password should be valid')
            return JsonResponse(data)

        new_data = auth.login(username,password)
        data = update_dict(data,new_data)

        print(data)

        response = JsonResponse(data)
        return response

@csrf_exempt
def authenticate(request):
    if 'username' in request.POST and 'auth_key' in request.POST:
        auth_token = {'username':request.POST['username'],'auth_key':request.POST['auth_key']}
        return JsonResponse({"autenticated":auth.authenticate(auth_token)})
    else:
        return JsonResponse({"msg":["login first"],"autenticated":False})
    
@csrf_exempt
def logout(request):
    response = JsonResponse({"msg":["Logged out successfully..."],'return_code':True})
    response.delete_cookie('username')
    response.delete_cookie('auth_key')
    print(request.COOKIES)
    return response