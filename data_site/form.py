"""
Functions and object to show and validate data for a json-schema.
"""
from flask import render_template, current_app

from jsonschema import validate, Draft7Validator as Validator
from jsonschema.exceptions import ValidationError

from data_site.form_schema import schema as FORM_SCHEMA

# '_schema' is a json-schema compliant schema (see https://json-schema.org/learn/)
# '_schema' is a python dictionary
_schema = None
# '_validator' holds a 'jsonschema' validator. Its content is dictated by '_schema'
_validator = None


def register_schema(schema):
    """
    Register 'schema' to be used with class::Validator. Set module variable ('_v'). Return None.
    """
    global _validator
    global _schema
    try:
        _tmp = Validator(schema)
    except Exception as err:
        _tmp = None
        raise err
    finally:
        _validator = _tmp
        _schema = schema if _validator else None
    return None

# Register an empty object (nothing to exibit)
# An empty '{}' json-schema is valid, it accepts everything
# (https://json-schema.org/understanding-json-schema/basics.html)
# but it has nothing to show for a form -- our purpose here.
register_schema({})
# A more meaningful (sample) schema would be:
register_schema({ 'type':'object', 'properties':{ 'test':{ 'type':'string' }}})
# , providing a field "test" of type "string" in our initial form.
register_schema(FORM_SCHEMA)

assert _validator, "Validator should be set here, with an useless content (empty), but set."


def parse(form_data):
    """
    Return 'form_data' with some values (eg, "number") parsed/cast (eg, "float")

    This function is applied to data comming from a web form and confronted with '_form'.
    Some values, like "number" (in the _form/_v schema), should be parsed,
    because everything from html/form/input come as string.
    """
    props = _schema['properties']
    out = form_data.copy()
    for name,value in form_data.items():
        if props[name]['type'] == 'number':
            try:
                out[name] = float(value)
            except:
                out[name] = 0
    return out


def validate(form_data, errors=None):
    """
    Return True if validation against schema registered, see function::register_schema()

    'form_data' is a key-value structure like: {'test':'Hi!'}
    """
    _vout = sorted(_validator.iter_errors(form_data), key=lambda e: e.path)
    if _vout:
        if errors is not None and isinstance(errors, list):
            for _err in _vout:
                prop = list(_err.path)[0]
                msg = _err.message
                errors.append(f"{prop} : {msg}")
        return False
    return None


def allowed_file(filename):
    ALLOWED_EXTENSIONS = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def render(metadata=None, files=None):
    """
    Render the form from 'properties' object in 'schema' (see json-schema.org)

    If 'values' is provided they will be used to fill the form fields.
    'values' is a dictionary of '{name : value}', where 'name' should match
    the 'schema['properties']' object.
    """
    if not 'properties' in _schema:
        return f"Schema is not valid: '{_schema}'"

    # values = []
    # for name,params in _schema['properties'].items():
    #     _v = {"name": name}
    #     _v['type'] = params['type']
    #     if metadata and name in metadata:
    #         _v['value'] = metadata[name]
    #     if 'enum' in params:
    #         _v['enum'] = params['enum']
    #     values.append(_v)
    #
    # _requireds = _schema['required'] if 'required' in _schema else None
    # return render_template('blog/create.html', fields=values, files=files, requireds=_requireds)
    return render_template('blog/create_hard.html', fields=metadata, files=files)
