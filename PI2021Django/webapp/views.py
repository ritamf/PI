import json
import secrets
import statistics

from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.http import HttpResponse
from django.shortcuts import render

from .serializers import sensorsSerializers# ,productsSerializers, attributesSerializers 

from django.core.cache import cache

from .models import Users, TokensTable

from DBoT import DB
from DBoT import JsonParser



# user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
# user.last_name = 'Lennon'
# #u = User.objects.get(username='john')
# user = authenticate(username='john', password='secret')
# user.save()

# {"name":"luis","email":"luis222@ua.pt","password":"vbnvbnvbn"}

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

    sObj = Users.if_not_exists().create(user_email_value=user_email, user_password_value=user_password)

    sObj2 = TokensTable.if_not_exists().create(user_email_value=user_email,user_token_value=secrets.token_urlsafe(32))

    return Response(sObj,sObj2)

# '/authenticate_user
@api_view(['POST'])
def authenticate_user_page(request):

    req = request.data

    user_email = req["email"]
    user_password = req["password"]

    print(user_email)
    print(user_password)

    userObj = Users.objects.get(user_email_value=user_email)

    if (userObj.user_password_value == user_password):
        sObj2 = TokensTable.objects(user_email_value=user_email).update(user_token_value=secrets.token_urlsafe(32))
        #authenticate_user_page.sObjToken = TokensTable.objects.get(user_email_value=user_email).user_token_value
        return Response('success')

    return Response('password or email invalid')

# '/insert_into_db
@api_view(['POST'])
def insert_into_db(request,user,sensorid):

    db = DB.DB()

    req = json.dumps(request.data)

    jsonParserInit = JsonParser.JsonParser()

    readJson = jsonParserInit.flat_json(req)

    db.insertIntoSensor(readJson, sensorid, user)

    return Response(readJson)

# '/query_db/<str:user>/<str:sensorid>'
@api_view(['POST'])
def query_db(request,user,sensorid):

    db = DB.DB()

    req = request.data

    #{"conditions": {"temperature": "=12"}, "attributes": ["temperature"]}
    #{"conditions": {"temperature": "=12"}, "attributes": ["temperature"], "from_ts": "2020-06-02 10:10:10", "to_ts": "2021-08-01 22:36:20.785976"} 2021-05-16 12:06:38.843256
    conditions = req["conditions"]
    print(conditions)
    attributes = req["attributes"]
    print(attributes)

    from_ts = req["from_ts"]
    to_ts = req["to_ts"]

    if sensorid != "all":
        if attributes is not None:
            if conditions is not None:
                if from_ts != "None" and from_ts != "":
                    values = db.rangeQueryPerSensor(user, sensorid, attributes, conditions, from_ts, to_ts)
                else:
                    print("didnt use ts")
                    values = db.queryPerSensor(user, sensorid, attributes, conditions)
            else:
                values = db.queryPerSensor(user, sensorid, attributes, {})
    else:
        if attributes is not None:
            if conditions is not None:
                if from_ts != "None" and from_ts != "":
                    values = db.rangeQueryPerUser(user, attributes, conditions, from_ts, to_ts)
                else:
                    values = db.queryPerUser(user, attributes, conditions)
            else:
                values = []
                for c in attributes:
                    dic = {c: db.getAllValuesOn(c)}
                    values.append(dic)

    return Response(values)

# '/get_sensor_attributes/<str:user>/<str:sensorid>
@api_view(['GET'])
def get_sensor_attributes(self,user,sensorid):

    db = DB.DB()

    sensor_attributes = db.getSensorAttributes(user,sensorid)

    attributes = [attribute for attributeList in sensor_attributes for attribute in attributeList[2] ]

    attributes = list(dict.fromkeys(attributes))
    print(attributes)

    return Response(attributes)

# '/get_all_attributes/<str:user>/
@api_view(['GET'])
def get_all_attributes(self):

    db = DB.DB()

    sensor_attributes = db.getAllSensorsAttributes()

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
        #'user_token': authenticate_user_page.sObjToken,
    }
    
    return render(request, "insert.html", context)

# '/query'
def db_query_page(request, *args, **kwargs):
    print(args, kwargs)

    db = DB.DB()

    sensors_list = db.getSensors('admin')

    
    context = {
        'user': 'admin',
        'sensors': sensors_list,
    }
    
    return render(request, "query.html", context)


# 'grafana/'
@api_view(['GET'])
def datasource_test(self):
    content = {'Test connection': 'datasource config page test'}
    #return Response(content, status=status.HTTP_200_OK)
    return Response(User.objects.get(username='luis'))

# 'grafana/search'
# COLEM ESTE JSON no post_search
#{ "target": "query field value" }
@api_view(['POST'])
def datasource_search(request):
    db = DB.DB()
    user = "Luis"

    req = request.data
    check_if_req_contains_type = "type" in req

    if check_if_req_contains_type == True:
        type_format = req["type"]
        target = req["target"]
    else:
        target = req["target"]

    sensores = ""
    sensor_list = db.getSensors(user)
    wordFormation = ""
    dropdown = []
    for sensores in sensor_list:
        dropdown.append(sensores)
        sensorAttributes = db.getSensorAttributes(user, sensores)
        #print(sensorAttributes)
        attributesList = sensorAttributes[0][2]
        for attributes in attributesList:
            
            if (attributes != "sensorid") and (attributes != "timestamp"):
                wordFormation = sensores + "." + attributes
                dropdown.append(wordFormation)
                print(dropdown)
    
    return Response(dropdown)

# 'grafana/query'
@api_view(['POST'])
def datasource_query(self, request):
    user = "Marta"  # need to know how we know who is logged in
    data = json.loads(request.data)
    db = DB.DB()
    ti = data['range.from']
    tf = data['range.to']
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


    tempo = ti - tf
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
        if sensor is not None and sensor != '':
            if campo is not None and campo != '':
                if condicoes is not None and condicoes != '':
                    values = db.rangeQueryPerSensor(user, sensor, campo, condicoes, ti, tf)
                else:
                    values = db.rangeQueryPerSensor(user, sensor, campo, {}, ti, tf)
        else:
            if campo is not None and campo != '':
                if condicoes is not None and condicoes != '':
                    values = db.rangeQueryPerUser(user, campo, condicoes, ti, tf)
                else:
                    values = db.rangeQueryPerUser(user, campo, {}, ti, tf)

        if req_type == 'table':
            results.extend(dataframe_to_json_table(target, values))
        else:
            results.extend(dataframe_to_response(target, values, intervalMs))

    return Response(results, status=status.HTTP_200_OK)


def dataframe_to_json_table(target, results):
    return None


def dataframe_to_response(target, results, freq, ti, tf):

    points = (tf - ti)/freq
    listofValues = []
    temporaryList = []
    sensor, campo = target['target'].split('.', 1)
    for dic in results:
        tfinal = ti + freq
        for p in range(points):
            while dic['timestamp'] in [ti, tfinal]:
                if tfinal > tf:
                    break
                point = [dic[campo], dic['timestamp']]
                temporaryList.append(point)
                point = statistics.mean(listofValues)
                listofValues.append(point)
                temporaryList = []
            ti = ti + freq
            tfinal = tfinal + freq



    response = {'target': target[target], 'datapoints': listofValues}
    return response

# 'grafana/annotations'
@api_view(['GET'])
def datasource_annotations(self):
    content = {'Test connection': 'datasource config page test'}
    return Response(content, status=status.HTTP_200_OK)


@api_view(['GET'])
def sensors_overview(request):
    api_urls = {
        'List': 'sensors/list/',
    }
    return Response(api_urls)


# sensors/create
@api_view(['POST'])
def sensors_post(request):
    db = DB.DB()
    json_file = request.data['json_file']
    sensor = request.data['sensor']
    user = "Marta"  # need to know who is logged in
    db.insertInto(json_file, sensor, user)
    return Response(status=status.HTTP_201_CREATED)

@api_view(['GET'])
def sensors_get(request):
    api_urls = {
        'List': 'sensors/list/',
    }
    return Response(api_urls)

@api_view(['GET'])
def sensors_get_one(request):
    api_urls = {
        'List': 'sensors/list/',
    }
    return Response(api_urls)





# @api_view(['GET'])
# def overview(request):
#     api_urls = {
#         'List': 'products/list/',
#         'Detail View': 'products/detail/<str:pk>/',
#         'Create': 'products/create/',
#         'Create From List': 'products/create_list/',
#         'Update': 'products/update/<str:pk>/',
#         'Delete': 'products/delete/<str:pk>/',
#     }
#     return Response(api_urls)


# @api_view(['POST'])
# def post(request):
#     sObj = products.if_not_exists().create(id=uuid.uuid4(), attributes=request.data)
#     return Response(sObj, status=status.HTTP_201_CREATED)


# @api_view(['POST'])
# def update(request, key):
#     sObj = products.objects(id=key).if_exists().update(attributes=request.data)
#     return Response(sObj, status=status.HTTP_201_CREATED)


# @api_view(['DELETE'])
# def delete(request, key):
#     res = products.objects.get(id=key)
#     res.delete()

#     return Response('Item succsesfully delete!')
