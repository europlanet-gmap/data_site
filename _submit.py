from flask import render_template

from jsonschema import validate, Draft7Validator as Validator
from jsonschema.exceptions import ValidationError


# FORM_TEMPLATE = [
#     {"name" : "username"},
#     {"name" : "age", "type": "number"}
# ]
FORM_SCHEMA = {
  "$id": "location.schema",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Longitude and Latitude Values",
  "description": "A geographical coordinate.",
  "required": [ "latitude", "longitude", "target" ],
  "type": "object",
  "properties": {
    "latitude": {
      "type": "number",
      "minimum": -90,
      "maximum": 90
    },
    "longitude": {
      "type": "number",
      "minimum": -180,
      "maximum": 180
    },
    "target": {
        "type": "string"
    },
    "comments": {
        "type": "string"
    }
  }
}




def register_schema(schema=FORM_SCHEMA):
    """
    Register 'schema' to be used with class::Validator. Return instance of Validator(schema)
    """
    global _v
    try:
        _tmp = Validator(schema)
    except Exception as err:
        raise err
    else:
        _tmp = None
    finally:
        _v = _tmp


_v = register_schema(FORM_SCHEMA)


def parse_form(form_data, form_schema = FORM_SCHEMA):
    """
    Return 'form_data' with some values (eg, "number") parsed/cast (eg, "float")

    Because everything from html/form/input come as strings, we should parse some.
    """
    props = form_schema['properties']
    out = form_data.copy()
    for name,value in form_data.items():
        if props[name]['type'] == 'number':
            out[name] = float(value)
    return out

def validate_form(form_data):
    """
    Return True if validation agains schema registered, see function::register_schema()
    """
    errors = sorted(_v.iter_errors(form_data), key=lambda e: e.path)
    if errors:
        msgs = {}
        for error in errors:
            prop = list(error.path)[0]
            msgs[prop] = msgs.get(prop, []) + [error.message]
        print(msgs)
        return False
    return True

def do_submit(form_template=None):
    return 'do_submit'

def show_form(error=None, schema=FORM_SCHEMA, values=None):
    assert schema['type'] == 'object'
    _schema = []
    for name,params in schema['properties'].items():
        _s = {"name": name}
        _s['type'] = params['type']
        if values and name in values:
            _s['value'] = values[name]
        _schema.append(_s)
    return render_template('submit.html', fields=_schema)
