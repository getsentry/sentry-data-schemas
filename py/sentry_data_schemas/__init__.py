from importlib.resources import path
from jsonschema_typed import JSONSchema

with path("sentry_data_schemas", "event.schema.json") as schema_path:
    EventData = JSONSchema["var:sentry_data_schemas:schema_path"]
