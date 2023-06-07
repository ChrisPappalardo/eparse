# -*- coding: utf-8 -*-

'''
excel parser interfaces
'''

from pprint import PrettyPrinter
from uuid import uuid4

import pandas as pd
from peewee import (
    AutoField,
    CharField,
    DatabaseProxy,
    fn,
    IntegerField,
    Model,
    SqliteDatabase,
)


DATABASE = DatabaseProxy()
SQLITE3_DATABASE = ''


class ExcelParse(Model):
    '''
    excel parse model
    '''

    id = AutoField()
    row = IntegerField()
    column = IntegerField()
    value = CharField()
    type = CharField()
    c_header = CharField()
    r_header = CharField()
    excel_RC = CharField()
    name = CharField()
    sheet = CharField()
    f_name = CharField()

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


def to_null(*args, **kwargs):
    '''
    do nothing with parse data
    '''

    pass


def to_stdout(data, *args, pretty=True, **kwargs):
    '''
    print parse data to stdout
    '''

    if pretty:
        PrettyPrinter().pprint(data)
    else:
        print(data)


def to_sqlite3(data, ctx, *args, **kwargs):
    '''
    inject parse data into sqlite3 database
    '''

    global DATABASE
    global SQLITE3_DATABASE

    # this output handler requires parse -z to work
    try:
        assert ctx.obj['serialize']
    except:
        raise Exception(f'serialize required for this interface')

    # create database if none was supplied
    if not SQLITE3_DATABASE:
        SQLITE3_DATABASE = f'.files/{uuid4()}.db'

    DATABASE.initialize(SqliteDatabase(SQLITE3_DATABASE))
    DATABASE.connect()
    DATABASE.create_tables([ExcelParse])

    # insert data into parse table
    for d in data:
        ExcelParse.create(**d)

    DATABASE.close()


def to_api(data, *args, **kwargs):
    '''
    post parse data to API endpoint
    '''

    pass


def from_sqlite3(db):
    '''
    factory to return ExcelParse model from sqlite3 db
    '''

    DATABASE.initialize(SqliteDatabase(db))
    DATABASE.connect()

    return ExcelParse
