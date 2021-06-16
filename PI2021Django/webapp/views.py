import json
import secrets
import hashlib
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from django.core.mail import send_mail
from datetime import datetime, timedelta
import statistics
from operator import itemgetter
import traceback
from django.views.decorators.csrf import csrf_exempt
import ast

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.http import HttpResponse
from django.shortcuts import render
from django import template

from django.core.cache import cache

from .models import TokensTable, TokensTable_secondary, Users, UserNamesTable
import logging

from DBoT import DB, Cache
from DBoT import JsonParser

cache = Cache.Cache(4)

print(cache.cachedElements.keys())

# '/register_user
@csrf_exempt
@api_view(['POST'])
def register_user_page(request):

    req = request.data

    user_name = req["name"]
    user_email = req["email"]
    user_password = req["password"]

    # try:
    #     user_name = UserNamesTable.objects.get(user_name_value=user_name).user_name_value
    # except:
    #     return Response("name already exists")

    try:
        h = hashlib.new('sha512_256')
        h.update(user_password.encode('utf-8'))
        h2 = hashlib.new('sha512_256')
        h2.update(user_email.encode('utf-8'))

        try:
            UserNamesTable.objects.get(user_name_value=user_name).user_name_value
            return Response("name already exists")
        
        except:
            try:
                Users.objects.get(user_email_value=h2.hexdigest()).user_name_value
                return Response("email already exists")

            except:
                try:
                    DB.register(user_name,h.hexdigest())
                    UserNamesTable.if_not_exists().create(user_name_value=user_name)
                    Users.if_not_exists().create(user_name_value=user_name, user_email_value=h2.hexdigest(),user_password_value=h.hexdigest())
                except:
                    return Response("There was an error, please try again")

    except:
        return Response("error")

    return Response("success")

# '/logout_user/<str:token>'
@csrf_exempt
@api_view(['GET'])
def logout_user_page(request,user_token):

    h = hashlib.new('sha512_256')

    h.update(user_token.encode('utf-8'))

    h_hexdigest = h.hexdigest()

    try:
        res = TokensTable.objects.get(user_token_value=h_hexdigest)
        res2 = TokensTable_secondary.objects.get(user_email_value=res.user_email_value)
        res2.delete()

        res.delete()
    
    except:
        return Response("invalid token")

    return Response("successfully logged out")

# '/authenticate_user
@csrf_exempt
@api_view(['POST'])
def authenticate_user_page(request):

    req = request.data

    user_email = req["email"]
    user_password = req["password"]

    h = hashlib.new('sha512_256')
    h.update(user_password.encode('utf-8'))

    h_hexdigest = h.hexdigest()

    h2 = hashlib.new('sha512_256')
    h2.update(user_email.encode('utf-8'))

    h2_hexdigest = h2.hexdigest()

    try:
        userObj = Users.objects.get(user_email_value=h2_hexdigest)

    except:
        return Response('email invalid')

    if (userObj.user_password_value == h_hexdigest):
        
        user_name = Users.objects.get(user_email_value=h2_hexdigest).user_name_value
        user_session = DB.sessionLogin(user_name,h_hexdigest)
        cache.add(user_session[0],user_session[1])
        
        print(cache.get(user_name))

        session_token = secrets.token_urlsafe(32) # token to use during session

        h2 = hashlib.new('sha512_256')

        h2.update(session_token.encode('utf-8'))

        h3 = hashlib.new('sha512_256')

        h3.update(user_email.encode('utf-8'))

        try: 
            user_token_outdated = TokensTable_secondary.objects.get(user_email_value=h3.hexdigest()).user_token_value
            TokensTable.objects.get(user_token_value=user_token_outdated).delete()
            TokensTable.create(user_email_value=h3.hexdigest(), user_token_value=h2.hexdigest())
            TokensTable_secondary.objects.get(user_email_value=h3.hexdigest()).update(user_token_value=h2.hexdigest())
        except:
            TokensTable.create(user_email_value=h3.hexdigest(), user_token_value=h2.hexdigest())
            TokensTable_secondary.create(user_email_value=h3.hexdigest(), user_token_value=h2.hexdigest())

        return Response(session_token)
    
    return Response('password invalid')

# '/insert_into_db
@csrf_exempt
@api_view(['POST'])
def insert_into_db(request,user_token,sensorid):

    print(cache.cachedElements.keys())

    req = request.data

    if (isinstance(req, list)):
        pass
    else:
        req = "[" + str(req) + "]";
        req = ast.literal_eval(req);

    jsonParserInit = JsonParser.JsonParser()

    parsedJson = []
    for item in req:
        jsonParserInit.flat_json(json.dumps(item))
        parsedJson.append(item)

    h2 = hashlib.new('sha512_256')

    h2.update(user_token.encode('utf-8'))

    try:
        user_email = TokensTable.objects.get(user_token_value=h2.hexdigest()).user_email_value
        user_name = Users.objects.get(user_email_value=user_email).user_name_value
        user_password = Users.objects.get(user_email_value=user_email).user_password_value
        sessCache = cache.get(user_name)
        #novo
        if sessCache is None:
            user_session = DB.sessionLogin(user_name,user_password)
            cache.add(user_session[0],user_session[1])
            sessCache = cache.get(user_name)
        
        DB.insertIntoSensor(sessCache,parsedJson, sensorid)
    
        return Response(parsedJson)
    
    except:
        return Response('invalid token')

# '/query_db/<str:sensorid>'
@csrf_exempt
@api_view(['POST'])
def query_db(request,user_token,sensorid):

    #db = DB.DB()

    req = request.data

    h2 = hashlib.new('sha512_256')

    h2.update(user_token.encode('utf-8'))

    h2_hexdigest = h2.hexdigest()

    try:
        user_email = TokensTable.objects.get(user_token_value=h2_hexdigest).user_email_value
        user_name = Users.objects.get(user_email_value=user_email).user_name_value
        user_password = Users.objects.get(user_email_value=user_email).user_password_value

        sessCache = cache.get(user_name)

        #novo
        if sessCache is None:
            user_session = DB.sessionLogin(user_name,user_password)
            cache.add(user_session[0],user_session[1])
            sessCache = cache.get(user_name)

        conditions = req["conditions"]

        attributes = req["attributes"]

        from_ts = req["from_ts"]
        to_ts = req["to_ts"]

        if h2_hexdigest == TokensTable.objects.get(user_email_value=user_email).user_token_value:

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
    except:
        return Response('invalid token')

# '/password_reset_request
@csrf_exempt
@api_view(['POST'])
def password_reset_request(request):

    req = request.data
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

# '/get_all_attributes/<str:user_token>
@csrf_exempt
@api_view(['GET'])
def get_all_attributes(request,user_token):

    h2 = hashlib.new('sha512_256')

    h2.update(user_token.encode('utf-8'))

    user_email = TokensTable.objects.get(user_token_value=h2.hexdigest()).user_email_value
    user_name = Users.objects.get(user_email_value=user_email).user_name_value
    user_password = Users.objects.get(user_email_value=user_email).user_password_value

    sessCache = cache.get(user_name)

    if sessCache is None:
        user_session = DB.sessionLogin(user_name,user_password)
        cache.add(user_session[0],user_session[1])
        sessCache = cache.get(user_name)

    #get all attributes
    all_attributes = DB.getAllSensorsAttributes(sessCache)

    all_attributes_2 = [attribute for attributeList in all_attributes for attribute in attributeList[2] ]

    all_attributes_2 = list(dict.fromkeys(all_attributes_2))

    attributes_dict = {"all": all_attributes_2}

    sensors_list = DB.getSensors(sessCache)

    for sensorid in sensors_list:

        sensor_attributes = DB.getSensorAttributes(sessCache,sensorid)

        sensor_attributes_2 = [attribute for attributeList in sensor_attributes for attribute in attributeList[2] ]

        sensor_attributes_2 = list(dict.fromkeys(sensor_attributes_2))

        attributes_dict[sensorid] = sensor_attributes_2
    
    return Response(attributes_dict)

# '/'
@csrf_exempt
def home_page(request, *args, **kwargs):
    print(args, kwargs)
    
    return render(request, "home.html", {})

# '/insert'
@csrf_exempt
def db_insert_page(request, *args, **kwargs):
    print(args, kwargs)

    return render(request, "insert.html", {})

# '/query'
@csrf_exempt
def db_query_page(request, *args, **kwargs):
    print(args, kwargs)
    
    return render(request, "query.html", {})

# '/token/<str:token>'
@csrf_exempt
def db_token_page(request, token):

    context = {
        'user_token': token,
    }
    
    return render(request, "token.html", context)


# '/logout'
@csrf_exempt
def logout_page(request, *args, **kwargs):
    print(args, kwargs)
    
    return render(request, "logout.html", {})

# '/recover_password_page'
@csrf_exempt
def recover_password_page(request, *args, **kwargs):
    print(args, kwargs)
    
    return render(request, "recover_password.html", {})

# '<str:user_token>/grafana'
@csrf_exempt
@api_view(['GET'])
def datasource_test(self,user_token):
    return Response(status.HTTP_200_OK)

# '<str:user_token>/grafana/search'
@csrf_exempt
@api_view(['POST'])
def datasource_search(request,user_token):

    h2 = hashlib.new('sha512_256')

    h2.update(user_token.encode('utf-8'))

    user_email = TokensTable.objects.get(user_token_value=h2.hexdigest()).user_email_value
    user_name = Users.objects.get(user_email_value=user_email).user_name_value
    user_password = Users.objects.get(user_email_value=user_email).user_password_value

    sessCache = cache.get(user_name)

    #novo
    if sessCache is None:
        user_session = DB.sessionLogin(user_name,user_password)
        cache.add(user_session[0],user_session[1])
        sessCache = cache.get(user_name)

    sensores = ""
    sensor_list = DB.getSensors(sessCache)
    wordFormation = ""
    dropdown = []
    dropdownUnique = []
    for sensores in sensor_list:
        sensorAttributes = DB.getSensorAttributes(sessCache, sensores)
        for form in sensorAttributes:
            attributesList = form[2]
            for attributes in attributesList:
                if (attributes != "sensorid") and (attributes != "timestamp"):
                    wordFormation = sensores + "." + attributes
                    dropdown.append(wordFormation)
                    if wordFormation not in dropdownUnique:
                        dropdownUnique.append(wordFormation)
    return Response(dropdownUnique)
    
# '<str:user_token>/grafana/query'
@csrf_exempt
@api_view(['POST'])
def datasource_query(request,user_token):
    try:
        print(request.body)
        h2 = hashlib.new('sha512_256')

        h2.update(user_token.encode('utf-8'))

        user_email = TokensTable.objects.get(user_token_value=h2.hexdigest()).user_email_value
        user_name = Users.objects.get(user_email_value=user_email).user_name_value
        user_password = Users.objects.get(user_email_value=user_email).user_password_value

        sessCache = cache.get(user_name)
        data = request.data
        ti = data['range']['from']
        tf = data['range']['to']

        target = data["targets"][0]

        condicoes = None
        intervalMs = None
        maxDataPoints = None
        if 'adhocFilters' in data:
            condicoes = []
            c = data['adhocFilters']
            for dic in c:
                param = dic['key']
                value = dic['value']
                condic = dic['operator']
                condicoes.append([param,condic,value])
        if 'intervalMs' in data:
            intervalMs = data['intervalMs']
        if 'maxDataPoints' in data:
            maxDataPoints = data['maxDataPoints']

        ti_ts = datetime.strptime(ti,"%Y-%m-%dT%H:%M:%S.%fZ")
        tf_ts = datetime.strptime(tf,"%Y-%m-%dT%H:%M:%S.%fZ")
        tempo = ti_ts - tf_ts
        tempo_seconds = tempo.total_seconds()

        tempo_miliseconds = tempo_seconds*1000
        dif_interval = tempo_miliseconds/maxDataPoints

        if dif_interval > intervalMs:
            intervalMs = dif_interval

        results = []

        req_type = target.get('type', 'timeserie')
        sensor, campo = target['target'].split('.', 1)

        if campo is None or campo == '':
            sensorAttributes = DB.getSensorAttributes(sessCache, sensor)
            campo = sensorAttributes[0][2]
        else:
            campo = [campo]
        if sensor is not None and sensor != '':
            if campo is not None and campo != '':
                if condicoes is not None:
                    values = DB.rangeQueryPerSensor(sessCache, sensor, campo, condicoes, ti, tf)
        else:
            if campo is not None and campo != '':
                if condicoes is not None:
                    print("rangeQueryPerUser")
                    values = DB.rangeQueryPerUser(sessCache, campo, condicoes, ti, tf)

        values_sorted = sorted(values, key=itemgetter('timestamp'))

        if req_type == 'table':
            results = dataframe_to_json_table(target, values_sorted, intervalMs, ti_ts, tf_ts)
        else:
            results = dataframe_to_response(target, values_sorted, intervalMs, ti_ts, tf_ts)
    
        return Response(results, status=status.HTTP_200_OK)
    except Exception as e:
        tb = traceback.format_exc()
        return Response(str(e) + " " + tb, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    if len(results) > 0:
        campos = list(results[0].keys())
        campos.remove("timestamp")
    else:
        campos = []

    point = ti

    for attribute in campos:
        response.append({"target":attribute , "datapoints" : []})

    point_counter = 0

    while point < tf:
        i = 0
        for attribute in campos:
            point_attribute_values = []
            for dic in results:
                timestamp = dic['timestamp']
                ts = datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S")
                if ts <= point + timedelta(seconds=freq / 1000) and ts>= point:
                    point_attribute_values.append(dic[attribute])
                else:
                    continue
            if len(point_attribute_values) > 0:
                print(point_attribute_values)
                point_attribute_average = sum(point_attribute_values) / len(point_attribute_values)
            else:
                point_attribute_average = 0
            
            response[i]['datapoints'].append([])
            response[i]['datapoints'][point_counter].append(point_attribute_average)
            response[i]['datapoints'][point_counter].append(to_epoch(point.strftime("%Y-%m-%dT%H:%M:%S.%fZ")))
            
            i = i+1
        point = point + timedelta(seconds=freq / 1000)
        point_counter += 1

    return response

# https://oznetnerd.com/2018/04/17/writing-a-grafana-backend-using-the-simple-json-datasource-flask/
def to_epoch(dt_format):
    epoch = int((datetime.strptime(dt_format, "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds()) * 1000
    return epoch

# '<str:user_token>/grafana/annotations'
@csrf_exempt
@api_view(['POST'])
def datasource_annotations(request,user_token):
    print(request.body)
    unix_epoch_time = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)
    content = {'text': 'text shown in body','time':unix_epoch_time}
    return Response(content)

# '<str:user_token>/grafana/tag-keys'
@csrf_exempt
@api_view(['POST'])
def datasource_tagkeys(self,user_token):
    h2 = hashlib.new('sha512_256')

    h2.update(user_token.encode('utf-8'))

    user_email = TokensTable.objects.get(user_token_value=h2.hexdigest()).user_email_value
    user_name = Users.objects.get(user_email_value=user_email).user_name_value
    user_password = Users.objects.get(user_email_value=user_email).user_password_value

    sessCache = cache.get(user_name)

    #novo
    if sessCache is None:
        user_session = DB.sessionLogin(user_name,user_password)
        cache.add(user_session[0],user_session[1])
        sessCache = cache.get(user_name)

    tagkeys_list = []

    all_attributes = DB.getAllSensorsAttributes(sessCache)

    all_attributes_2 = [attribute for attributeList in all_attributes for attribute in attributeList[2] ]

    all_attributes_2 = list(dict.fromkeys(all_attributes_2))

    for i in all_attributes_2:
        tagkeys_list.append({"type":"string","text":i})
    
    return Response(tagkeys_list)

# '<str:user_token>/grafana/tag-values'
@csrf_exempt
@api_view(['POST'])
def datasource_tagvalues(request,user_token):
    h2 = hashlib.new('sha512_256')

    h2.update(user_token.encode('utf-8'))

    user_email = TokensTable.objects.get(user_token_value=h2.hexdigest()).user_email_value
    user_name = Users.objects.get(user_email_value=user_email).user_name_value
    user_password = Users.objects.get(user_email_value=user_email).user_password_value

    sessCache = cache.get(user_name)

    if sessCache is None:
        user_session = DB.sessionLogin(user_name,user_password)
        cache.add(user_session[0],user_session[1])
        sessCache = cache.get(user_name)

    req = request.data

    tag_value_key = req["key"]

    tag_value_key_list = [tag_value_key]

    values = DB.queryPerUser(sessCache, tag_value_key_list, [])

    tagvalue_list = []

    for i in values:

        tagvalue_temp = {"test": str(i[tag_value_key])}

        if tagvalue_temp not in tagvalue_list:
            tagvalue_list.append(tagvalue_temp)
    
    return Response(tagvalue_list)
