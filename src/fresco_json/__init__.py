"""
Utilities for serializing to/from JSON.

Objects that are JSON serializable need to be adapted to
:class:`zenzero.interfaces.IJSONDumpable`.

"""
from __future__ import absolute_import

import json
from collections import MutableMapping
from functools import wraps, partial
from operator import attrgetter

from zope.interface import Interface
from fresco import context, POST, PUT
from fresco import Response
from fresco.util.http import parse_header
from fresco.util.io import SizeLimitedInput

__version__ = '0.1dev'
__all__ = 'IJSONDumpable', 'IJSONLoadable', 'json_dump', \
          'json_load', 'json_dumps', 'json_loads'


class IJSONDumpable(Interface):
    """
    IJSONDumpable objects are suitable to be serialized to representations
    such as JSON
    """

    def to_json_repr(self):
        """
        Return the object reduced to python primitives (dicts,
        lists, ints, floats, strings, bools and None).
        """
        raise NotImplementedError()


class IJSONLoadable(Interface):
    """
    IJSONLoadable objects are suitable to be serialized to representations
    such as JSON
    """

    def to_python(self):
        """
        Return the object reduced to python primitives (dicts,
        lists, ints, floats, strings, bools and None).
        """
        raise NotImplementedError()


def parse_json_input(environ, default_charset='UTF-8'):

    c_type, c_params = parse_header(environ.get('CONTENT_TYPE',
                                                'application/json'))
    charset = c_params.get('charset', default_charset)

    assert c_type == 'application/json', c_type

    c_length = int(environ['CONTENT_LENGTH'])

    if c_length > context.request.MAX_SIZE:
        raise ValueError("Content Length exceeds permitted size")

    return json.load(SizeLimitedInput(environ['wsgi.input'], c_length),
                     charset)


def json_view():
    def json_view(view_func):
        """
        Wrap ``view_func`` to make consuming and returning json formatted data
        trivial.

        On ingress, automatically parse any ``application/json`` type request
        body as a json string, or a request var named ``json``.

        On egress, automatically encode the response as json. If ``callback``
        was specified in the request, the response will be wrapped as a jsonp
        callback.
        """
        def json_view(*args, **kwargs):
            request = context.request
            environ = request.environ
            data = None

            # Already run in this request?
            if 'fresco_json.data' in request.environ:
                kwargs.setdefault('data',
                                  environ['fresco_json.data'])
            elif environ['REQUEST_METHOD'] in (POST, PUT):
                if environ.get('CONTENT_TYPE', '')\
                   .startswith('application/json'):
                    data = parse_json_input(environ)
                elif 'data' in request.form:
                    data = json_loads(request.form.get('data'))
                if data is not None:
                    kwargs['data'] = data
                    environ['fresco_json.data'] = data

            result = view_func(*args, **kwargs)

            json_str = json_dumps(result)
            cb = request.query.get('callback')
            if cb is not None:
                json_str = '%s(%s)' % (cb, json_str)
            return Response(content_type='application/json',
                            content=[json_str])
        try:
            return wraps(view_func)(json_view)
        except TypeError:
            return json_view
    return json_view


def json_dump_default(ob, dumper=json.dumps):
    adapter = IJSONDumpable(ob, None)

    if adapter is None:
        return ob

    result = adapter.to_json_repr()

    if not isinstance(result, MutableMapping):
        raise AssertionError("Expected a MutableMapping, got %r" % (result,))

    result['__json_class__'] = (adapter.__class__.__module__ + '.' +
                                adapter.__class__.__name__ + ':' +
                                ob.__class__.__module__ + '.'
                                + ob.__class__.__name__)
    return result


def class_by_name(name):
    parts = name.split('.')
    module = __import__('.'.join(parts[:-1]))
    return attrgetter('.'.join(parts[1:]))(module)


def json_load_object_hook(data):
    if '__json_class__' in data:
        adapter_class, ob_class = map(class_by_name,
                                      data.pop('__json_class__').split(':'))
        adapter = adapter_class(None)
        return adapter.to_python(ob_class, data)
    return data

json_dump = partial(json.dump, default=json_dump_default)
json_dumps = partial(json.dumps, default=json_dump_default)
json_load = partial(json.load, object_hook=json_load_object_hook)
json_loads = partial(json.loads, object_hook=json_load_object_hook)
