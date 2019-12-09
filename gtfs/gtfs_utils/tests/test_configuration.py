import json
import os

from ..gtfs_utils.configuration import validate_configuration_schema, get_json_schema

DESCRIPTION_KEYS = ('title', 'description', '$$description', '$$title')


def test_example_config():
    example_config = json.load(open(os.path.join(os.path.dirname(__file__),
                                                 '../gtfs_utils/config_example.json')))
    validate_configuration_schema(example_config)


def validate_description(key_name, schema_item):
    if 'type' in schema_item:
        assert not set(DESCRIPTION_KEYS).isdisjoint(schema_item.keys()), \
                f'{key_name!r} key in the JSON Schema has no description'
        if schema_item['type'] == 'object':
            assert 'properties' in schema_item
            for key, value in schema_item['properties'].items():
                validate_description(key, value)
        if 'definitions' in schema_item:
            for key, value in schema_item['definitions'].items():
                validate_description(key, value)


def test_configuration_documentation():
    schema = get_json_schema()
    validate_description('schema', schema)
