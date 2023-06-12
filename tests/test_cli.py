#!/usr/bin/env python

'''
unit tests for eparse cli
'''

from click.testing import CliRunner
import pytest

from eparse.cli import main


kwargs = {'obj': {}, 'catch_exceptions': False}


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'Usage' in result.output


def test_output_option():
    runner = CliRunner()
    result = runner.invoke(main, ['-o', 'null:///', 'scan'], **kwargs)
    assert result.exit_code == 0
    assert result.output == ''
    result = runner.invoke(main, ['-o', 'spoon', 'scan'], **kwargs)
    assert result.exit_code == 1
    assert 'there is no spoon' in result.output
    with pytest.raises(AttributeError):
        result = runner.invoke(main, ['-d', '-o', 'spoon', 'scan'], **kwargs)
