"""
Submit holds the functions and object to show and validate data for a json-schema.
"""
from flask import render_template

from jsonschema import validate, Draft7Validator as Validator
from jsonschema.exceptions import ValidationError

import backend


# '_form' is a json-schema compliant schema (see https://json-schema.org/learn/)
# '_form' is a python dictionary
_form = None
# '_v' holds a 'jsonschema' validator. Its content is dictated by '_form'
_v = None

def register_schema(schema):
    """
    Register 'schema' to be used with class::Validator. Set module variable ('_v'). Return None.
    """
    global _v
    global _form
    try:
        _tmp = Validator(schema)
    except Exception as err:
        _tmp = None
        raise err
    finally:
        _v = _tmp
        _form = schema if _v else None
    return None

# Register an empty object (nothing to exibit)
# An empty '{}' json-schema is valid, it accepts everything
# (https://json-schema.org/understanding-json-schema/basics.html)
# but it has nothing to show for a form -- our purpose here.
register_schema({})
# A more meaningful (sample) schema would be:
register_schema({ 'type':'object', 'properties':{ 'test':{ 'type':'string' }}})
# , providing a field "test" of type "string" in our initial form.
assert _v, "Validator should be set here, with an useless content (empty), but set."


def parse_form(form_data):
    """
    Return 'form_data' with some values (eg, "number") parsed/cast (eg, "float")

    This function is applied to data comming from a web form and confronted with '_form'.
    Some values, like "number" (in the _form/_v schema), should be parsed,
    because everything from html/form/input come as string.
    """
    form_schema=_form
    props = form_schema['properties']
    out = form_data.copy()
    for name,value in form_data.items():
        if props[name]['type'] == 'number':
            try:
                out[name] = float(value)
            except:
                out[name] = 0
    return out


def validate_form(form_data):
    """
    Return True if validation against schema registered, see function::register_schema()

    'form_data' is a key-value structure like: {'test':'Hi!'}
    """
    validator=_v
    errors = sorted(validator.iter_errors(form_data), key=lambda e: e.path)
    if errors:
        msgs = {}
        for error in errors:
            prop = list(error.path)[0]
            msgs[prop] = msgs.get(prop, []) + [error.message]
        print(msgs)
        return False
    return True


def do_submit(metadata, files, files_path):
    return backend.compose_package(metadata, files, files_path)

def show_form(error=None, metadata=None, files=None):
    """
    Render the form from 'properties' object in 'schema' (see json-schema.org)

    If 'values' is provided they will be used to fill the form fields.
    'values' is a dictionary of '{name : value}', where 'name' should match
    the 'schema['properties']' object.
    """
    schema = _form
    if not 'properties' in schema:
        return f"Schema is not valid: '{schema}'"

    _schema = []
    for name,params in schema['properties'].items():
        _s = {"name": name}
        _s['type'] = params['type']
        if metadata and name in metadata:
            _s['value'] = metadata[name]
        if 'enum' in params:
            _s['enum'] = params['enum']
        _schema.append(_s)
    return render_template('submit.html.j2', fields=_schema, files=files)
