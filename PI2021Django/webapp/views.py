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
    db = DB.DB()
    user = "Marta"

    req = json.loads(request.data)
    target = req["target"]

    if ':' in target:
        finder, target = target.split(':', 1)
    else:
        finder = target

    if not target or finder not in metric_finders:
        metrics = []
        if target == '*':
            metrics += metric_finders.keys() + metric_readers.keys()
        else:
            metrics.append(target)

        return json_dump(metrics)
    else:
        return json_dump(list(metric_finders[finder](target)))

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
