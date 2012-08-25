#from nose.tools import assert_equal
from storm.locals import Storm, Int, Unicode
from fresco_json import stormadapter  # NOQA
#from fresco_json import json_dumps, json_loads
from zope import component


class Model(Storm):

    __storm_table__ = ''

    column_a = Int(primary=1)
    column_b = Unicode()


class TestStormAdapter(object):

    def test_dumpable(self):

        m = Model()
        m.column_a = 5
        m.column_b = u'xyz'

        adapter = component.getAdapter(m, stormadapter.IJSONDumpable)
        assert adapter.to_json_repr() == \
            {'column_a': 5,
             'column_b': 'xyz'}

    def test_loadable(self):

        js = {'column_a': 5, 'column_b': u'xyz'}

        m = Model()
        adapter = component.getAdapter(m, stormadapter.IJSONLoadable)
        adapter.from_json_repr(js)
        assert m.column_a == 5
        assert m.column_b == u'xyz'
