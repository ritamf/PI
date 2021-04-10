```bash
pip install requirements.txt

CREATE KEYSPACE "db" WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3};

CREATE TABLE db.products (id UUID PRIMARY KEY. attributes Map<>);

```

```bash
source bin/activate

python manage.py runserver
```