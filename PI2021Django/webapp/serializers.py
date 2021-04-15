from cassandra.cqlengine import columns
from rest_framework import serializers
from .models import sensors
from .models import metadata  
#, products


class sensorsSerializers(serializers.ModelSerializer):
    serializer_field_mapping = (
        serializers.ModelSerializer.serializer_field_mapping.copy()
    )
    serializer_field_mapping[columns.UUID] = columns.UUID

    # serializer_field_mapping[columns.Map] = columns.Map

    class Meta:
        model = sensors
        fields = '__all__'

    def to_representation(self, obj):
        return {
            "sensor_id": str(obj.sensor_id),
            "user": str(obj.user),
            "tables": obj.tables,
            "pks": obj.pks,
        }

class metadataSerializers(serializers.ModelSerializer):
    serializer_field_mapping = (
        serializers.ModelSerializer.serializer_field_mapping.copy()
    )
    serializer_field_mapping[columns.UUID] = columns.UUID

    # serializer_field_mapping[columns.Map] = columns.Map

    class Meta:
        model = metadata
        fields = '__all__'

    def to_representation(self, obj):
        return {
            "table_name": str(obj.table_name),
            "table_attributes": str(obj.table_attributes),
        }


# class productsSerializers(serializers.ModelSerializer):
#     serializer_field_mapping = (
#         serializers.ModelSerializer.serializer_field_mapping.copy()
#     )
#     serializer_field_mapping[columns.UUID] = columns.UUID

#     # serializer_field_mapping[columns.Map] = columns.Map

#     class Meta:
#         model = products
#         fields = '__all__'

#     def to_representation(self, obj):
#         attribs = []
#         for attribute in obj.attributes:
#             attribs.append({
#                 str(attribute): obj.attributes[attribute]
#             })
#         return {
#             "id": str(obj.id),
#             "attributes": attribs,
#         }
