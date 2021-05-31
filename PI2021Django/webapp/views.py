import json
import secrets
import hashlib
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from django.core.mail import send_mail

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.http import HttpResponse
from django.shortcuts import render
from django import template

from .serializers import sensorsSerializers# ,productsSerializers, attributesSerializers 

from django.core.cache import cache

from .models import TokensTable, Users

from DBoT import DB, Cache
from DBoT import JsonParser

cache = Cache.Cache(1)

print(cache.cachedElements.keys())

# '/register_user
@api_view(['POST'])
def register_user_page(request):

    req = request.data

    user_name = req["name"]
    user_email = req["email"]
    user_password = req["password"]

    print(user_name)
    print(user_email)
    print(user_password)

    try:
        h = hashlib.new('sha512_256')
        h.update(user_password.encode('utf-8'))
        #h.hexdigest()
        sObj = Users.if_not_exists().create(user_name_value=user_name, user_email_value=user_email,user_password_value=h.hexdigest())
    except:
        return Response("user already exists")

    DB.register(user_name,h.hexdigest())

    return Response("success")

# '/logout_user
@api_view(['GET'])
def logout_user_page(request):

    res = TokensTable.objects.get(user_name_value=request.session.get('username'))
    res.delete()

    request.session.flush()

    return Response("successfully logged out")

# '/authenticate_user
@api_view(['POST'])
def authenticate_user_page(request):

    req = request.data

    user_email = req["email"]
    user_password = req["password"]

    h = hashlib.new('sha512_256')
    h.update(user_password.encode('utf-8'))
    
    userObj = Users.objects.get(user_email_value=user_email)

    if (userObj.user_password_value == h.hexdigest()):
        
        user_name = Users.objects.get(user_email_value=user_email).user_name_value
        user_session = DB.sessionLogin(user_name,h.hexdigest())
        cache.add(user_session[0],user_session[1])
        
        print(cache.get(user_name))

        session_token = secrets.token_urlsafe(32) # token to use during session

        h = hashlib.new('sha512_256')

        h.update(session_token.encode('utf-8'))
        
        TokensTable.create(user_name_value=user_name, user_token_value=h.hexdigest())
       
        #request.session['token'] = session_token
        request.session['username'] = user_name
        request.session['usermail'] = user_email
        #request.session['token'].set_expiry(0)

        return Response(session_token)

    

    return Response('password or name invalid')

# '/insert_into_db
@api_view(['POST'])
def insert_into_db(request,user_token,sensorid):

    print(cache.cachedElements.keys())

    req = json.dumps(request.data)

    jsonParserInit = JsonParser.JsonParser()

    readJson = jsonParserInit.flat_json(req)

    sessCache = cache.get(request.session.get('username'))

    if sessCache is None:
        print(request.session.get('username'))
        print(Users.objects.get(user_email_value=request.session.get('usermail')).user_password_value)
        user_session = DB.sessionLogin(request.session.get('username'),Users.objects.get(user_email_value=request.session.get('usermail')).user_password_value)
        cache.add(user_session[0],user_session[1])
        sessCache = cache.get(request.session.get('username'))

    h = hashlib.new('sha512_256')

    h.update(user_token.encode('utf-8'))
    
    #if user_token == request.session.get('token'):
    if h.hexdigest() == TokensTable.objects.get(user_name_value=request.session.get('username')).user_token_value:
        DB.insertIntoSensor(sessCache,readJson, sensorid)
    
    else:
        print("yoyo")
        return Response("invalid token")
    
    # if sessCache == None:
    #     user_name = Users.objects.get(user_name_value=user_name).user_name_value
    #     user_session = DB.sessionLogin(user_name,token)
    #     cache.add(user_session[0],user_session[1])
    return Response(readJson)

# '/query_db/<str:sensorid>'
@api_view(['POST'])
def query_db(request,user_token,sensorid):

    #db = DB.DB()

    req = request.data

    sessCache = cache.get(request.session.get('username'))

    conditions = req["conditions"]

    attributes = req["attributes"]

    from_ts = req["from_ts"]
    to_ts = req["to_ts"]

    h = hashlib.new('sha512_256')

    h.update(user_token.encode('utf-8'))
    
    #if user_token == request.session.get('token'):
    if h.hexdigest() == TokensTable.objects.get(user_name_value=request.session.get('username')).user_token_value:

        if sensorid != "all":
            if attributes is not None:
                if conditions is not None:
                    if from_ts != "None" and from_ts != "":
                        values = DB.rangeQueryPerSensor(sessCache, sensorid, attributes, conditions, from_ts, to_ts)
                    else:
                        print("didnt use ts")
                        values = DB.queryPerSensor(sessCache, sensorid, attributes, conditions)
                else:
                    values = DB.queryPerSensor(sessCache, sensorid, attributes, {})
        else:
            if attributes is not None:
                if conditions is not None:
                    if from_ts != "None" and from_ts != "":
                        values = DB.rangeQueryPerUser(sessCache, attributes, conditions, from_ts, to_ts)
                    else:
                        values = DB.queryPerUser(sessCache, attributes, conditions)
                else:
                    values = []
                    for c in attributes:
                        dic = {c: DB.getAllValuesOn(c)}
                        values.append(dic)
    else:
        return Response("invalid token")

    return Response(values)

# '/password_reset_request
@api_view(['POST'])
def password_reset_request(request):

    req = request.data
    #{"input_email":"nekolapras@gmail.com"}
    input_email = req["input_email"]

    if Users.objects.get(user_email_value=input_email) is not None: #verificar seexiste uma conta com este mail
	    
	    subject = "Password Reset Requested"
	    htmltemp = template.loader.get_template('reset_password_email.html')
	    c = { 
	    "email": input_email,
	    'domain':'127.0.0.1:8000',
	    'site_name': 'Website',
	    'new_password': secrets.token_urlsafe(32),
	    'protocol': 'http',
	    }
	    html_content = htmltemp.render(c)

	    send_mail(subject, html_content, 'Website <lvalentim@ua.pt>', [input_email], fail_silently=False)


    return Response("success")

# '/get_sensor_attributes/<str:sensorid>
@api_view(['GET'])
def get_sensor_attributes(request,sensorid):

    sessCache = cache.get(request.session.get('username'))

    sensor_attributes = DB.getSensorAttributes(sessCache,sensorid)

    attributes = [attribute for attributeList in sensor_attributes for attribute in attributeList[2] ]

    attributes = list(dict.fromkeys(attributes))
    print(attributes)

    return Response(attributes)

# '/get_all_attributes/
@api_view(['GET'])
def get_all_attributes(request):

    sessCache = cache.get(request.session.get('username'))

    sensor_attributes = DB.getAllSensorsAttributes(sessCache)

    attributes = [attribute for attributeList in sensor_attributes for attribute in attributeList[2] ]

    attributes = list(dict.fromkeys(attributes))
    print(attributes)

    return Response(attributes)


# '/get_user_current_token/<str:user_email>
@api_view(['GET'])
def get_user_current_token_page(self,user_email):

    sObjToken = TokensTable.objects.get(user_email_value=user_email).user_token_value

    info = {"email": user_email, "token": sObjToken}

    return Response(info)
    

# '/'
def home_page(request, *args, **kwargs):
    print(args, kwargs)
    
    return render(request, "home.html", {})

# '/insert'
def db_insert_page(request, *args, **kwargs):
    print(args, kwargs)

    context = {
        'user': 'admin',
        'sensorid': 1,
    }
    
    return render(request, "insert.html", context)

# '/query'
def db_query_page(request, *args, **kwargs):
    print(args, kwargs)

    sessCache = cache.get(request.session.get('username'))

    if sessCache is None:
        print(request.session.get('username'))
        print(Users.objects.get(user_email_value=request.session.get('usermail')).user_password_value)
        user_session = DB.sessionLogin(request.session.get('username'),Users.objects.get(user_email_value=request.session.get('usermail')).user_password_value)
        cache.add(user_session[0],user_session[1])
        sessCache = cache.get(request.session.get('username'))

    sensors_list = DB.getSensors(sessCache)

    context = {
        'user': 'admin',
        'sensors': sensors_list,
    }
    
    return render(request, "query.html", context)

# '/token/<str:token>'
def db_token_page(request, token):

    context = {
        'user': 'admin',
        'sensorid': 1,
        'user_token': token,
    }
    
    return render(request, "token.html", context)


# '/logout'
def logout_page(request, *args, **kwargs):
    print(args, kwargs)
    
    return render(request, "logout.html", {})

# '/recover_password_page'
def recover_password_page(request, *args, **kwargs):
    print(args, kwargs)
    
    return render(request, "recover_password.html", {})


# 'grafana/'
@api_view(['GET'])
def datasource_test(self):
    return Response(status.HTTP_200_OK)

# 'grafana/search'
#{ "target": "query field value" }
@api_view(['POST'])
def datasource_search(request):

    sessCache = cache.get(request.session.get('username'))

    req = request.data
    check_if_req_contains_type = "type" in req

    if check_if_req_contains_type == True:
        type_format = req["type"]
        target = req["target"]
    else:
        target = req["target"]

    sensores = ""
    sensor_list = DB.getSensors(sessCache)
    wordFormation = ""
    dropdown = []
    for sensores in sensor_list:
        dropdown.append(sensores)
        sensorAttributes = DB.getSensorAttributes(sessCache, sensores)
        #print(sensorAttributes)
        attributesList = sensorAttributes[0][2]
        for attributes in attributesList:
            
            if (attributes != "sensorid") and (attributes != "timestamp"):
                wordFormation = sensores + "." + attributes
                dropdown.append(wordFormation)
                if attributes not in dropdown:
                    dropdown.append(attributes)
    
    return Response(np.array(dropdown))
    
# 'grafana/query'
@api_view(['GET'])
def datasource_query(self):
    content = {'Test connection': 'datasource config page test'}
    return Response(content, status=status.HTTP_200_OK)

# 'grafana/annotations'
@api_view(['GET'])
def datasource_annotations(self):
    content = {'Test connection': 'datasource config page test'}
    return Response(content, status=status.HTTP_200_OK)
