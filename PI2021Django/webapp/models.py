import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.management import sync_table
from django_cassandra_engine.models import DjangoCassandraModel
# from viewfow.fields import CompositeKey

class Users(DjangoCassandraModel):
    user_name_value = columns.Text()
    user_email_value = columns.Text(primary_key=True)
    user_password_value = columns.Text()

class TokensTable(DjangoCassandraModel):
    user_email_value = columns.Text()
    user_token_value = columns.Text(primary_key=True)

class TokensTable_secondary(DjangoCassandraModel):
    user_email_value = columns.Text(primary_key=True)
    user_token_value = columns.Text()