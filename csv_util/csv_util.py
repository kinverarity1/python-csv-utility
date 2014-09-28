import csv
try:
    import cStringIO as StringIO
except:
    import StringIO

import numpy



class Csv(object):
    """Utility class for reading/writing CSV files.

    Args:
        - *fn*: CSV filename
        - *delimiter*: character (default ,); set to " " for whitespace-delimited files.
        - *comment*: ignore lines beginning with this (default #)
        - *numeric*: attempt to convert values to floats

    Methods:
        - *reload*: reload file
        - *keys*: get column titles
        - *values*: get column values as lists of strings
        - *items*: zip(keys(), values())
        - *float*: get column values as ndarray of floats, if possible
    
    You can access column values as lists using the ``[key]`` syntax on the
    class object, which behaves like a dictionary. The keys() method gives 
    a list of column headers.

    Attributes:
        - *delimiter*
        - *fn*
        - *txt*: text of CSV file (actually this is used rather than *fn* to
          read data from. You can definitely set this attribute directly if you like.)
        - *f*: file-like object built from *txt*, read-only
        - *DictReader*: :class:`csv.DictReader` object
        - *table*: list of list of string objects, each inner list is a row of the CSV
        - *ndarray*: convert table into an numpy ndarray (fails if there is
          non-numerical data in the CSV)

    """
    def __init__(self, fn=None, fo=None, text=None, 
                 delimiter=',', comment='#', numeric=True,
                 quotechar='"'):
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.comment = comment
        self.numeric = numeric
        if not text is None:
            self.text = text
        elif not fn is None:
            fo = open(fn, mode='r')
            self.fn = fn
        if fo:
            self.text = fo.read()
            fo.close()

    def _v(self, value):
        if self.numeric:
            try:
                return float(value)
            except:
                if value == '':
                    return numpy.nan
                else:
                    return value
        else:
            return value

    def __len__(self):
        return len(self.rows)

    @property
    def f(self):
        newlines = []
        lines = self.text.splitlines()
        for line in lines:
            if not line.strip().startswith(self.comment):
                newlines.append(line)        
        return StringIO.StringIO('\n'.join(newlines))

    @property
    def DictReader(self):
        return csv.DictReader(self.f, delimiter=self.delimiter)

    def keys(self):
        return self.DictReader.fieldnames

    def __getitem__(self, key):
        key = str(key)
        if not key in self.keys():
            raise KeyError('Key %s not found' % key)
        else:
            return [self._v(row[key]) for row in self.DictReader]

    def append(self, other):
        newlines = []
        for rowdict in other.rowsdict:
            line = []
            for key in self.keys():
                try:
                    line.append(str(rowdict[key]))
                except KeyError:
                    line.append('')
            newlines.append(self.delimiter.join(line))
        self.text += '\n' + '\n'.join(newlines)

    def float(self, key):
        return numpy.asarray([float(i) for i in self.__getitem__(key)])

    def values(self):
        return [map(self._v, self[key]) for key in self.keys()]

    def items(self):
        return zip(self.keys(), self.values())

    def _aslist(self, rowdict):
        return [rowdict[key] for key in self.keys()]

    @property
    def rows(self):
        return [map(self._v, self._aslist(row)) for row in self.DictReader]
    
    @property
    def rowsdict(self):
        return [dict(zip(self.keys(), r)) for r in self.rows]

    @property
    def ndarray(self):
        return numpy.asarray([[numpy.float(i) for i in row] for row in self.table[1:]])

    def get(self, query, field_names=None):
        '''Search CSV for *query* and return a dictionary for the row that it's
        found in. Optional: *field_names* restricts the columns in which *query*
        will be looked for.'''
        fieldnames = self.DictReader.fieldnames
        if field_names is None:
            field_names = fieldnames
        for field_name in field_names:
            try:
                assert field_name in fieldnames
            except AssertionError:
                raise KeyError('%s is not a column name' % field_name)
        for rowdict in self.DictReader:
            for field, value in rowdict.items():
                if value == query and field in field_names:
                    return dict(((key, self._v(value)) for key, value in rowdict.items()))
        return {}

    def subset(self, column, value=None, func=None):
        '''Return subset of rows where the value under *column* == *value* (or func(val) is True)'''
        cindex = self.keys().index(column)
        txtlines = [self.text.split('\n')[0]]
        if func is None:
            func = lambda val: val == value
        for row in self.rows:
            if func(row[cindex]):
                txtlines.append(self.delimiter.join(map(str, row)))
        return Csv(text='\n'.join(txtlines), delimiter=self.delimiter, numeric=self.numeric)

    def _sort(self, col=None, func=None):
        '''Return text version of CSV, sorted by *col*.'''
        if col:
            key = lambda r: r[col]
        else:
            if func:
                key = func
            else:
                key = None
        rowdicts = sorted(self.rowsdict, key=key)
        return self._rowdicts2string(rowdicts)

    def _rowdicts2string(self, rowdicts=None):
        if rowdicts is None:
            rowdicts = self.rowsdict
        fo = StringIO.StringIO()
        dict_writer = csv.DictWriter(fo, self.keys(), lineterminator='\n')
        dict_writer.writeheader()
        dict_writer.writerows(rowdicts)
        return fo.getvalue()

    def sort(self, **kws):
        '''Sort by col=column header, or func=lambda rowdict: ...'''
        self.text = self._sort(**kws)

    def sorted(self, **kws):
        '''Return new CSV object sorted by col=column header, or func=lambda rowdict: ...'''
        return Csv(text=self._sort(**kws))

    def add_column(self, header, values):
        assert len(values) == len(self.values()[0])
        newlines = []
        for i, line in enumerate(self.text.splitlines()):
            line = line.strip('\n').strip()
            if i == 0:
                if self.delimiter in header:
                    header = self.quotechar + header + self.quotechar
                line += self.delimiter + header
            else:
                value = str(values[i - 1])
                if self.delimiter in value:
                    value = self.quotechar + value + self.quotechar
                line += self.delimiter + value
            newlines.append(line)
        self.text = '\n'.join(newlines)

    def write(self, fo, **kwargs):
        '''Write CSV object to file-like object *fo*.'''
        fo.write(self._rowdicts2string())