# -*- coding: utf-8 -*-

'''
excel parser interfaces
'''

from abc import abstractmethod
from collections.abc import Iterable, Mapping
from datetime import datetime
from pprint import PrettyPrinter
import re
from typing import Dict, Optional
from uuid import uuid4

import pandas as pd
from peewee import (
    AutoField,
    CharField,
    DatabaseProxy,
    DateTimeField,
    fn,
    IntegerField,
    Model,
    SqliteDatabase,
)


DATABASE = DatabaseProxy()


class ExcelParse(Model):
    '''
    excel parse model
    '''

    id = AutoField()
    row = IntegerField()
    column = IntegerField()
    value = CharField()
    type = CharField()
    c_header = CharField(index=True)
    r_header = CharField(index=True)
    excel_RC = CharField(index=True)
    name = CharField(index=True)
    sheet = CharField(index=True)
    f_name = CharField(index=True)
    timestamp = DateTimeField(default=datetime.utcnow)

    @classmethod
    def get_queryset(cls, *args, **kwargs):
        '''
        return queryset with filters applied
        '''

        query = cls.filter(**kwargs)
        return pd.DataFrame(query.dicts())

    @classmethod
    def get_column(cls, column, *args, **kwargs):
        '''
        return distinct values from column with aggregations
        '''

        query = (
            cls
            .filter(**kwargs)
            .select(
                getattr(cls, column),
                fn.COUNT(cls.id).alias('Total Rows'),
                fn.COUNT(cls.type.distinct()).alias('Data Types'),
                fn.COUNT(cls.value.distinct()).alias('Distinct Values'),
            )
            .group_by(getattr(cls, column))
        )
        return pd.DataFrame(query.dicts())

    class Meta:
        database = DATABASE
        indexes = (
            (('f_name', 'sheet', 'name'), False),
        )


class BaseInterface:
    '''
    base interface class
    '''

    endpoint = ''
    user = ''
    password = ''
    host = ''
    port = 0
    name = ''

    Model = None

    def __init__(self, uri: str, Model: Optional[Model]=None):
        for k, v in self.parse_uri(uri).items():
            setattr(self, k, v)
        self.Model = Model

    @abstractmethod
    def input(self):
        '''
        from_X override with input handler
        '''

        pass

    @abstractmethod
    def output(self, data: pd.DataFrame, obj: Dict) -> pd.DataFrame:
        '''
        to_X override with output handler
        '''

        pass

    @classmethod
    def parse_uri(self, uri: str) -> Dict:
        '''
        parse eparse URI string
        '''

        patt = r'^(?P<endpoint>.*)://(?P<user>.*?)(:(?P<password>.*?))?(@(?P<host>.*?)(:(?P<port>.*?))?)?/(?P<name>.*)?$'  # noqa
        return re.match(patt, uri).groupdict()


class NullInterface(BaseInterface):
    '''
    null interface
    '''

    def input(self):
        return pd.DataFrame()

    def output(self, *args, **kwargs):
        pass


class StdoutInterface(BaseInterface):
    '''
    stdout interface
    '''

    def input(self):
        return pd.DataFrame()

    def output(self, data, *args, **kwargs):
        PrettyPrinter().pprint(data)


class Sqlite3Interface(BaseInterface):
    '''
    sqlite3 interface
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.name:
            self.name = f'.files/{uuid4()}.db'

    def input(self, method, **kwargs):
        m = getattr(self.Model, method, None)

        # if no explicit method is available, try get_column
        if m is None:
            m = self.Model.get_column
            patt = r'^(?:get_)?(?P<column>.*)$'
            kwargs['column'] = re.match(patt, method).group('column')

        DATABASE.initialize(SqliteDatabase(self.name))
        DATABASE.connect()

        return m(**kwargs)

    def output(self, data, obj):
        # skip empty data
        if hasattr(data, 'empty') and data.empty:
            return
        elif not hasattr(data, 'empty') and not data:
            return

        # check that data is serialized
        try:
            assert isinstance(data, Iterable)
            assert isinstance(data[0], Mapping)
        except:
            raise ValueError('bad data - did you serialize it first?')

        DATABASE.initialize(SqliteDatabase(self.name))
        DATABASE.connect()
        DATABASE.create_tables([self.Model])

        # insert data into Model
        for d in data:
            self.Model.create(**d)

        # DATABASE.close()


def i_factory(uri, Model=None):
    '''
    return interface object based on uri
    '''

    if uri.startswith('null'):
        return NullInterface(uri)
    elif uri.startswith('stdout'):
        return StdoutInterface(uri)
    elif uri.startswith('sqlite3'):
        return Sqlite3Interface(uri, Model)

    raise ValueError(f'{uri} is not a recognized endpoint')
