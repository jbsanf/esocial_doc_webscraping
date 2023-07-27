import os
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

db = TinyDB(
    os.path.join(os.getenv("DATA_PATH"), 'db.json'),
    storage=serialization,
)
tbl_arquivos = db.table('arquivos')