import json
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from DBoT import DB
from .models import sensors #, products, attributes
from .serializers import sensorsSerializers# ,productsSerializers, attributesSerializers 

from django.core.cache import cache

# 'grafana/'
@api_view(['GET'])
def datasource_test(self):
    content = {'Test connection': 'datasource config page test'}
    return Response(content, status=status.HTTP_200_OK)

# 'grafana/search'
@api_view(['POST'])
def datasource_search(request):
    if request.method == 'POST':
        return Response({"data": request.data})
    return Response([{"message": "Hello, world!"}])

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

@api_view(['GET'])
def sensors_get(request):
    user = "Marta"  # need to know how we know who is logged in
    db = DB.DB()
    # localhost/sensor=/search/by=campo
    if 'sensor' in request.GET:
        sensor = request.GET['sensor']
        if 'campo' in request.GET:
            campo = request.GET['campo']  # need to make sure is a list
            if 'param' in request.GET:
                param = request.GET['param']  # need to make sure is a dict
                values = db.queryPerSensor(user, sensor, campo, param)
            else:
                values = db.queryPerSensor(user, sensor, campo, {})
        else:
            values = db.queryPerSensor(user, sensor, ['*'], {})
    else:
        if 'campo' in request.GET:
            campo = request.GET['campo']
            if 'param' in request.GET:
                param = request.GET['param']  # need to make sure is a dict
                values = db.queryPerUser(user, campo, param)
            else:
                values = []
                for c in campo:
                    v = db.getAllValuesOn(c)
                    values.append(v)

        else:
            values = db.getSensors(user)

    if 'count' in request.GET:
        values = len(values)

    #return JsonResponse(values) ?? nao sei o que tenho que retornar


# sensors/create
@api_view(['POST'])
def sensors_post(request):
    db = DB.DB()
    json_file = request.data['json_file']
    sensor = request.data['sensor']
    user = "Marta"  # need to know who is logged in
    db.insertInto(json_file, sensor, user)
    return Response(status=status.HTTP_201_CREATED)




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