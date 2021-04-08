from flask import render_template

from jsonschema import validate, Draft7Validator as Validator
from jsonschema.exceptions import ValidationError


_v = None
_form = None

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


register_schema({})
assert _v, "Validator should be set here, with an useless content (empty), but set."

def parse_form(form_data):
    """
    Return 'form_data' with some values (eg, "number") parsed/cast (eg, "float")

    Because everything from html/form/input come as strings, we should parse some.
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
    Return True if validation agains schema registered, see function::register_schema()
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

def do_submit(form_template=None):
    return 'do_submit'

def show_form(error=None, values=None):
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
        if values and name in values:
            _s['value'] = values[name]
        if 'enum' in params:
            _s['enum'] = params['enum']
        _schema.append(_s)
    return render_template('submit.html', fields=_schema)
