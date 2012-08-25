from storm.expr import Column
from storm.locals import Storm

from zope import interface, component

from . import IJSONDumpable
from . import IJSONLoadable


class StormDumper(object):

    interface.implements(IJSONDumpable)
    component.adapts(Storm)

    def __init__(self, context):
        self.context = context

    def to_json_repr(self):
        columns = list(
            name for name in dir(self.context.__class__)
            if isinstance(getattr(self.context.__class__, name), Column)
        )

        return dict((key, getattr(self.context, key)) for key in columns)


class StormLoader(object):

    interface.implements(IJSONLoadable)
    component.adapts(Storm)

    def __init__(self, context):
        self.context = context

    def from_json_repr(self, jsondict):
        for k, v in jsondict.items():
            setattr(self.context, k, v)

component.provideAdapter(StormDumper)
component.provideAdapter(StormLoader)
