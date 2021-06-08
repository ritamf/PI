from cassandra.cqlengine import columns
from rest_framework import serializers

class sensorsSerializers(serializers.ModelSerializer):
    serializer_field_mapping = (
        serializers.ModelSerializer.serializer_field_mapping.copy()
    )
    serializer_field_mapping[columns.UUID] = columns.UUID