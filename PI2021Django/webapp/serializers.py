from cassandra.cqlengine import columns
from rest_framework import serializers

class sensorsSerializers(serializers.ModelSerializer):
    serializer_field_mapping = (
        serializers.ModelSerializer.serializer_field_mapping.copy()
    )
    serializer_field_mapping[columns.UUID] = columns.UUID

    # serializer_field_mapping[columns.Map] = columns.Map



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
