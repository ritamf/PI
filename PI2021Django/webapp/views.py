import json
import secrets
import hashlib
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from django.core.mail import send_mail
import requests
from datetime import datetime, timedelta
import statistics
from operator import itemgetter

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


# 'get_current_session/'
@api_view(['GET'])
def get_current_session(request):
    user_session_name = request.session.get('username')
    print(user_session_name)
    json_object = {"user_session_name": str(user_session_name)}
    return Response(json.dumps(json_object))

# 'grafana/'
@api_view(['GET'])
def datasource_test(self):
    return Response(status.HTTP_200_OK)

# 'grafana/search'
#{ "target": "query field value" }
@api_view(['POST'])
def datasource_search(request):
    #sessCache = cache.get(request.session.get('username'))

    # user_session_name = requests.get("http://127.0.0.1:8000/get_current_session")
    # sessCache = cache.get(user_session_name.json())

    sessCache = cache.get('cfe0')
    
    if sessCache is None:
        print(Users.objects.get(user_email_value=request.session.get('usermail')).user_password_value)
        user_session = DB.sessionLogin(request.session.get('username'),Users.objects.get(user_email_value=request.session.get('usermail')).user_password_value)
        cache.add(user_session[0],user_session[1])
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
        dropdown.append(sensores + ".")
        sensorAttributes = DB.getSensorAttributes(sessCache, sensores)
        #print(sensorAttributes)
        attributesList = sensorAttributes[0][2]
        for attributes in attributesList:
            
            if (attributes != "sensorid") and (attributes != "timestamp"):
                wordFormation = sensores + "." + attributes
                dropdown.append(wordFormation)
                if attributes not in dropdown:
                    dropdown.append("." + attributes)
                    
    
    #return Response(np.array(dropdown))
    return Response(dropdown)
    
# 'grafana/query'
@api_view(['POST'])
def datasource_query(request):
    sessCache = cache.get('cfe0')
    data = request.data
    ti = data['range']['from']
    tf = data['range']['to']
    condicoes = None
    intervalMs = None
    maxDataPoints = None
    if 'adhocFilters' in data:
        condicoes = {}
        c = data['adhocFilters']
        for dic in c:
            param = dic['key']
            condic = dic['operator'] + dic['value']
            condicoes[param] = condic
    if 'intervalMs' in data:
        intervalMs = data['intervalMs']
    if 'maxDataPoints' in data:
        maxDataPoints = data['maxDataPoints']

    #ti = datetime.strptime(ti,"%Y-%m-%dT%H:%M:%S.%fZ")
    #tf = datetime.strptime(tf,"%Y-%m-%dT%H:%M:%S.%fZ")
    ti_ts = datetime.strptime(ti,"%Y-%m-%d %H:%M:%S")
    tf_ts = datetime.strptime(tf,"%Y-%m-%d %H:%M:%S")
    tempo = ti_ts - tf_ts
    tempo_seconds = tempo.total_seconds()
    tempo_miliseconds = tempo_seconds*1000
    dif_interval = tempo_miliseconds/maxDataPoints

    if dif_interval > intervalMs:
        intervalMs = dif_interval

    results = []

    for target in data['targets']:

        req_type = target.get('type', 'timeserie')
        # targets é tudo o que aparece no mesmo dashboard
        sensor, campo = target['target'].split('.', 1)

        if campo is None or campo == '':
            sensorAttributes = DB.getSensorAttributes(sessCache, sensor)
            campo = sensorAttributes[0][2]
        else:
            campo = [campo]
        if sensor is not None and sensor != '':
            if campo is not None and campo != '':
                if condicoes is not None and condicoes != '':
                    values = DB.rangeQueryPerSensor(sessCache, sensor, campo, condicoes, ti, tf)
                else:
                    values = DB.rangeQueryPerSensor(sessCache, sensor, campo, {}, ti, tf)
        else:
            if campo is not None and campo != '':
                if condicoes is not None and condicoes != '':
                    values = DB.rangeQueryPerUser(sessCache, campo, condicoes, ti, tf)
                else:
                    values = DB.rangeQueryPerUser(sessCache, campo, {}, ti, tf)

        values_sorted = sorted(values, key=itemgetter('timestamp'))

        if req_type == 'table':
            results.append(dataframe_to_json_table(target, values_sorted, intervalMs, ti_ts, tf_ts))
        else:
            results.append(dataframe_to_response(target, values_sorted, intervalMs, ti_ts, tf_ts))

    return Response(results, status=status.HTTP_200_OK)


def dataframe_to_json_table(target, results, freq, ti, tf):

    dic_response = {"columns": [], "rows": [], "type": "table"}
    tinicial = results[0]['timestamp']
    tinicial = datetime.strptime(tinicial,"%Y-%m-%d %H:%M:%S")
    listofValues = []
    temporaryList = []

    tempo = (tf - ti)
    tempo_seconds = tempo.total_seconds()
    tempo_miliseconds = tempo_seconds*1000
    points = tempo_miliseconds / freq

    print(points)

    array_campo = results[0].keys()

    for p in range(points):
        
        point = []
        tfinal = tinicial + freq

        for c in array_campo:
            dic_response['columns'].append({'type': 'string', 'Text': c})

            for dic in results:
                while dic['timestamp'] in [tinicial, tfinal]:
                    temporaryList.append(dic[c])
            point.append(statistics.mean(temporaryList))
            temporaryList = []

        listofValues.append(point)
        if tfinal > tf:
            break
        tinicial = tinicial + freq

    response = [dic_response]

    return response


def dataframe_to_response(target, results, freq, ti, tf):
    
    response = []

    tinicial = results[0]['timestamp']
    tinicial = datetime.strptime(tinicial,"%Y-%m-%d %H:%M:%S")
    campos = results[0].copy()
    campos.pop("timestamp")
    array_campo = campos.keys()

    tempo = (tf - ti)
    tempo_seconds = tempo.total_seconds()
    tempo_miliseconds = tempo_seconds*1000
    points = int(tempo_miliseconds / freq)

    for c in array_campo:

        listofValues = []
        temporaryList = []

        for p in range(points):

            point = []
            tfinal = tinicial + timedelta(seconds=freq/1000)

            while results is not None:
                for dic in results:
                    timestamp = datetime.strptime(dic['timestamp'],"%Y-%m-%d %H:%M:%S")
                    print(timestamp)
                    print(tinicial)
                    print(tfinal)
                    print("yo")
                    if timestamp in [tinicial, tfinal]:
                            print(dic[c])
                            temporaryList.append(dic[c])
                            print(temporaryList)
                            results.remove(dic)                   
                    point.append(statistics.mean(temporaryList))
                    print(point)
                    temporaryList = []
                listofValues.append(point)
            
            print(temporaryList)
            value = statistics.mean(temporaryList)
            point = [value, tfinal]
            listofValues.append(point)
            temporaryList = []

            if tfinal > tf:
                break
            tinicial = tinicial + freq

        response.append({'target': target[target], 'datapoints': listofValues})

    return response

# 'grafana/annotations'
@api_view(['GET'])
def datasource_annotations(self):
    content = {'Test connection': 'datasource config page test'}
    return Response(content, status=status.HTTP_200_OK)
