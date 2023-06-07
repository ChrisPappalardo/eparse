#!/usr/bin/env python

'''
unit tests for eparse
'''

import pandas as pd
import pytest

from eparse.core import df_find_tables


@pytest.fixture
def xlsx():
    '''
    excel file fixture
    '''

    return pd.read_excel(
        'tests/eparse_unit_test_data.xlsx',
        header=None,
        index_col=None,
    )


def test_df_find_tables(xlsx):
    assert df_find_tables(xlsx)
