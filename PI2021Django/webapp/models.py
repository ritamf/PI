import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.management import sync_table
from django_cassandra_engine.models import DjangoCassandraModel


class sensors(DjangoCassandraModel):
    sensor_id = columns.Text(primary_key=True)
    user = columns.Text()
    tables = columns.List(value_type=columns.Text)
    pks = columns.List(value_type=columns.Text)

    class Meta:
        unique_together = (('sensor_id', 'user'))

class metadata(DjangoCassandraModel):
    table_name = columns.Text(primary_key=True)
    table_attributes = columns.List(value_type = columns.Text)


# Examples
# class products(DjangoCassandraModel):
#     id = columns.UUID(primary_key=True)
#     attributes = columns.Map(key_type=columns.Text, value_type=columns.Text)

#     def __str__(self):
#         return str(self.id)
# 
# class ExampleModel(DjangoCassandraModel):
#     example_id    = columns.UUID(primary_key=True, default=uuid.uuid4)
#     example_type  = columns.Integer(index=True)
#     created_at    = columns.DateTime()
#     description   = columns.Text(required=False)
