import csv
from datetime import datetime

from mudbug.mdbreader import mdb_action

class ManualHeaderReader(csv.DictReader):
    def __init__(self, source, columns, encoding=None, *args, **kw):
        self.encoding = encoding
        csv.DictReader.__init__(self, source, columns, *args, **kw)

    def next(self):
        row = csv.DictReader.next(self)
        if self.encoding is not None:
            for key, value in row.items():
                if isinstance(value, str):
                    row[key] = value.decode(self.encoding)
        return row

class HeaderReader(ManualHeaderReader):
    def __init__(self, csv_file, encoding=None, *args, **kw):
        first_line = csv.reader(csv_file, *args, **kw).next()
        columns = [title.strip() for title in first_line]
        ManualHeaderReader.__init__(self, csv_file, columns, encoding=encoding,
                                    *args, **kw)

class Row(dict):
    """
    >>> from pprint import pprint

    >>> r = Row(dict(one=u'1', two=u'2'))
    >>> r.one, r['one'], r.two, r['two']
    (u'1', u'1', u'2', u'2')

    >>> class Row2(Row):
    ...     int_fields = 'id', 'one', 'two',
    ...     bool_fields = 'is_big',
    ...

    >>> s = Row2(dict(id='15', one=u'1', two=u'2', is_big=u'1', other=u'o'))
    >>> pprint(s)
    {'id': 15, 'is_big': True, 'one': 1, 'other': u'o', 'two': 2}
    """
    int_fields = ()
    bool_fields = ()
    datetime_fields = ()

    def __init__(self, d):
        for b in self.bool_fields: d[b] = d[b] == u'1'
        for i in self.int_fields:
            try: d[i] = int(d[i])
            except ValueError: d[i] = None
        for dt in self.datetime_fields:
            try: d[dt] = datetime.strptime(d[dt], '%Y-%m-%d %H:%M:%S')
            except ValueError: d[dt] = None
        dict.__init__(self, d)

    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        except KeyError:
            return self[attr]

    def __getitem__(self, key):
        if isinstance(key, (tuple, list)):
            return tuple(self[k] for k in key)
        else:
            return dict.__getitem__(self, key)

class Table(object):
    def __init__(self, database, tablename, rowclass=Row):
        self.database = database
        self.tablename = tablename
        self.rowclass = rowclass
        self._rows = None

    @property
    def rows(self):
        if self._rows is None:
            rowstream = mdb_action(
                'export -D "%Y-%m-%d %k:%M:%S"',
                self.database.mdbpath,
                self.tablename)
            rowdicts = HeaderReader(rowstream, encoding='UTF-8')
            self._rows = [self.rowclass(row) for row in rowdicts]
        return self._rows

class Mdb(object):
    def __init__(self, mdbpath):
        self.mdbpath = mdbpath
        self.tables = dict((tablename, Table(self, tablename))
                           for tablename in
                           mdb_action('tables', self.mdbpath).read().split())
