#!/usr/bin/env python

'''
unit tests for eparse interfaces
'''

from peewee import SqliteDatabase
import pytest

from eparse.interfaces import (
    DATABASE,
    SQLITE3_DATABASE,
    ExcelParse,
    parse_uri,
    to_null,
    to_stdout,
)


@pytest.fixture
def ctx():
    '''
    click style ctx object fixture
    '''

    class Obj():
        obj = {}

    return Obj()


@pytest.fixture
def data():
    '''
    serialized data fixture
    '''

    return dict(
        row=0,
        column=0,
        value='test',
        type='test',
        c_header='test',
        r_header='test',
        excel_RC='A1',
        name='test',
        sheet='test',
        f_name='test',
    )


@pytest.fixture
def sqlite3_db(data):
    '''
    sqlite3 in-memory database fixture
    '''

    global DATABASE
    global SQLITE3_DATABASE

    SQLITE3_DATABASE = ':memory:'
    DATABASE.initialize(SqliteDatabase(SQLITE3_DATABASE))
    DATABASE.connect()
    DATABASE.create_tables([ExcelParse])

    ExcelParse.create(**data)

    return ExcelParse._meta.database.obj


def test_sqlite3_db(sqlite3_db):
    assert isinstance(sqlite3_db, SqliteDatabase)
    assert sqlite3_db.table_exists('excelparse')
    assert len(ExcelParse.select()) == 1


def test_ExcelParse_model(sqlite3_db):
    assert ExcelParse.get_queryset().shape == (1, 12)
    assert ExcelParse.get_column('c_header').shape == (1, 4)


def test_to_null():
    assert to_null() == None


def test_to_stdout():
    assert to_stdout({'foo'}) == None


def test_parse_uri():
    db = 'endpoint://user:password@host:port/name'
    p = parse_uri(db)
    keys = ('endpoint', 'user', 'password', 'host', 'port', 'name')
    not_keys = ()
    assert all([k in p.keys() for k in (keys + not_keys)])
    assert all([k in p.values() for k in keys])
    assert all([k not in p.values() for k in not_keys])
    db = 'endpoint://user@host/name'
    p = parse_uri(db)
    keys = ('endpoint', 'user', 'host', 'name')
    not_keys = ('password', 'port')
    assert all([k in p.keys() for k in (keys + not_keys)])
    assert all([k in p.values() for k in keys])
    assert all([k not in p.values() for k in not_keys])
    db = 'endpoint:///name'
    p = parse_uri(db)
    keys = ('endpoint', 'name')
    not_keys = ('user', 'password', 'host', 'port')
    assert all([k in p.keys() for k in (keys + not_keys)])
    assert all([k in p.values() for k in keys])
    assert all([k not in p.values() for k in not_keys])
    db = 'endpoint:///'
    p = parse_uri(db)
    keys = ('endpoint',)
    not_keys = ('user', 'password', 'host', 'port', 'name')
    assert all([k in p.keys() for k in (keys + not_keys)])
    assert all([k in p.values() for k in keys])
    assert all([k not in p.values() for k in not_keys])
