import json
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser

from .models import sensors #, products, attributes
from .serializers import sensorsSerializers# ,productsSerializers, attributesSerializers 

from django.core.cache import cache

from Libs import DB

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

#sensors/list
@api_view(['GET'])
def sensors_get(request):
    sensor = sensors.objects.all()
    searlizer = sensorsSerializers(sensor, many=True)
    return Response(searlizer.data)

#sensors/details/<str:pk>
@api_view(['GET'])
def sensors_get_one(request, key):
    sensor = sensors.objects.get(sensor_id=key)
    searlizer = sensorsSerializers(sensor, many=False)
    return Response(searlizer.data)

#sensors/create
@api_view(['POST'])
def sensors_post(request):
    sensor = sensors.if_not_exists().create(
        sensor_id=request.data['sensor_id'],
        user=request.data['user'],
        tables=request.data['tables'],
        pks=request.data['pks']
    )
    return Response(sensor, status=status.HTTP_201_CREATED)



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