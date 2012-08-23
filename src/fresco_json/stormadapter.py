from storm.expr import Column
from storm.locals import Storm

from zope.interface import implements
from zope.component import adapts

from . import IJSONDumpable
from . import IJSONLoadable


class StormSerializer(object):
    implements(IJSONDumpable)
    implements(IJSONLoadable)
    adapts(Storm)

    def __init__(self, context):
        self.context = context

    def to_json_repr(self):
        columns = list(
            name for name in dir(self.context.__class__)
            if isinstance(getattr(self.context.__class__, name), Column)
        )
        return dict((key, getattr(self.context, key)) for key in columns)

    def to_python(self):
        pass

