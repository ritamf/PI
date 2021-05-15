import json
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser

from django.http import HttpResponse
from django.shortcuts import render

from .models import sensors #, products, attributes
from .serializers import sensorsSerializers# ,productsSerializers, attributesSerializers 

from django.core.cache import cache

from DBoT import DB
from DBoT import JsonParser

# '/insert_test'
@api_view(['POST'])
def db_insert_test(request,user,sensorid):

    db = DB.DB()

    req = json.dumps(request.data)

    jsonParserInit = JsonParser.JsonParser()

    readJson = jsonParserInit.flat_json(req)

    db.insertIntoSensor(readJson, sensorid, user)

    return Response(readJson)

# '/'
def home_page(request, *args, **kwargs):
    print(args, kwargs)
    
    return render(request, "home.html", {})

# '/insert'
def db_insert(request, *args, **kwargs):
    print(args, kwargs)

    context = {
        'user': 'testuser',
        'sensorid': 1,
    }
    
    return render(request, "insert.html", context)

# '/query'
def db_query(request, *args, **kwargs):
    print(args, kwargs)
    
    return render(request, "query.html", {})


# 'grafana/'
@api_view(['GET'])
def datasource_test(self):
    content = {'Test connection': 'datasource config page test'}
    return Response(content, status=status.HTTP_200_OK)

# 'grafana/search'
@api_view(['POST'])
def datasource_search(request):
    # if request.method == 'POST':
    #     return Response({"data": request.data})
    # return Response([{"message": "Hello, world!"}])
    req = request.data
    check_if_req_contains_type = "type" in req

    if check_if_req_contains_type == True:
        type_format = req["type"]
        target = req["target"]
    else:
        target = req["target"]

    return Response(target)

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
