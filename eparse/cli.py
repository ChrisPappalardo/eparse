# -*- coding: utf-8 -*-

'''
excel parser cli module
'''

import click
import importlib
from pathlib import Path
from pprint import PrettyPrinter
import re
import sys

import pandas as pd

from .core import df_find_tables, df_parse_table, df_serialize_table


@click.group()
@click.pass_context
@click.option(
    '--input', '-i',
    type=str,
    multiple=True,
    help='input dir(s) or file(s)',
)
@click.option(
    '--output', '-o',
    type=str,
    default='to_null',
    help='output destination',
)
@click.option(
    '--debug', '-d',
    is_flag=True,
    default=False,
    help='use debug mode',
)
@click.option(
    '--loose', '-l',
    is_flag=True,
    default=True,
    help='find tables loosely',
)
@click.option(
    '--recursive', '-r',
    is_flag=True,
    default=False,
    help='find files recursively',
)
@click.option(
    '--truncate', '-t',
    is_flag=True,
    default=True,
    help='truncate dataframe output',
)
@click.option(
    '--verbose', '-v',
    count=True,
    help='increase output verbosity',
)
def main(ctx, input, output, debug, loose, recursive, truncate, verbose):
    '''
    excel parser
    '''

    ctx.obj['input'] = input
    ctx.obj['output'] = output
    ctx.obj['debug'] = debug
    ctx.obj['loose'] = loose
    ctx.obj['recursive'] = recursive
    ctx.obj['truncate'] = truncate
    ctx.obj['verbose'] = verbose

    files = []

    # get target file(s)
    for i in input:
        if Path(i).is_dir():
            g = '**/*' if recursive else '*'
            files += Path(i).glob(g)
        elif Path(i).is_file():
            files.append(Path(i))

    ctx.obj['files'] = files

    if ctx.obj['verbose']:
        print(f'found {len(files)} files')

    # set output function
    try:
        m = importlib.import_module('eparse.interfaces')
        ctx.obj['output_fcn'] = getattr(m, output)
    except AttributeError as e:
        print(f'output error - there is no {output}')
        if ctx.obj['debug']:
            raise
        sys.exit(1)

    # set truncate option
    if not truncate:
        # pd.set_option('display.max_colwidth', None)
        pd.set_option('display.max_rows', None)


@main.command()
@click.pass_context
@click.option(
    '--number', '-n',
    type=int,
    default=None,
    help='stop after n excel files',
)
@click.option(
    '--sheet', '-s',
    type=str,
    default=None,
    help='name of sheet to scan for',
)
@click.option(
    '--tables', '-t',
    is_flag=True,
    default=False,
    help='count tables in scanned sheets',
)
def scan(ctx, number, sheet, tables):
    '''
    scan for excel files in target
    '''

    ctx.obj['number'] = number
    ctx.obj['sheet'] = sheet
    ctx.obj['tables'] = tables

    if ctx.obj['debug']:
        PrettyPrinter().pprint(ctx.obj)

    # process each Excel file in files
    for i, f in enumerate(ctx.obj['files']):
        if f.is_file() and 'xls' in f.name:

            try:
                e_file = pd.read_excel(
                    f, sheet_name=sheet, header=None, index_col=None
                )
            except Exception as e:
                print(f'skipping {f} due to {e}')
                if not ctx.obj['debug']:
                    continue
                raise

            # get basic info about Excel file
            f_size_mb = f.stat().st_size / 1_024_000
            sheets = []

            if type(e_file) is dict:
                sheets = e_file.keys()

            # build output result based on options selected
            result = f'{f.name}'

            if ctx.obj['verbose']:
                result += f' {f_size_mb:.2f}MB'

            if sheet is not None:
                result += f' with {sheet} {e_file.shape}'

                if tables:
                    t = df_find_tables(e_file, ctx.obj['loose'])
                    result += f' containing {len(t)} tables'

                    if ctx.obj['verbose'] > 1:
                        result += f' ({t})'

            else:
                if ctx.obj['verbose']:
                    result += f' with {len(sheets)} sheets'

                if ctx.obj['verbose'] > 1 and len(sheets):
                    result += f' {",".join(sheets)}'

            # print result
            print(result)

            if ctx.obj['debug']:
                PrettyPrinter().pprint(e_file)

            # continue if number has not been reached
            if number is not None and i >= number:
                break


@main.command()
@click.pass_context
@click.option(
    '--sheet', '-s',
    type=str,
    multiple=True,
    help='name of sheet(s) to parse',
)
@click.option(
    '--serialize', '-z',
    is_flag=True,
    default=False,
    help='serialize table output',
)
@click.option(
    '--table', '-t',
    type=str,
    default=None,
    help='name of table to parse',
)
def parse(ctx, sheet, serialize, table):
    '''
    parse table(s) found in sheet for target(s)
    '''

    ctx.obj['sheet'] = sheet
    ctx.obj['serialize'] = serialize
    ctx.obj['table'] = table

    if ctx.obj['debug']:
        PrettyPrinter().pprint(ctx.obj)

    # process each Excel file in files
    for i, f in enumerate(ctx.obj['files']):
        if f.is_file() and 'xls' in f.name:

            try:
                e_file = pd.read_excel(
                    f,
                    sheet_name=list(sheet) or None,
                    header=None,
                    index_col=None,
                )
            except Exception as e:
                print(f'skipping {f} due to {e}')
                if not ctx.obj['debug']:
                    continue
                raise

            if not ctx.obj['verbose']:
                print(f'{f.name}')

            # convert e_file to dict if single sheet
            if type(e_file) is not dict:
                e_file = {s: e_file for s in sheet}

            # process each table found in each sheet of file
            for s in e_file.keys():
                for r, c, excel_RC, name in df_find_tables(
                    e_file[s],
                    ctx.obj['loose'],
                ):
                    if table is not None and table.lower() not in name.lower():
                        continue

                    # parse and serialize (if enabled) table
                    output = df_parse_table(e_file[s], r, c)

                    if ctx.obj['verbose']:
                        m = '{} table {} {} found at {} in {}'
                        v = (f.name, name, output.shape, excel_RC, s)
                        print(m.format(*v))

                    if serialize:
                        output = df_serialize_table(
                            output,
                            name=str(name),
                            sheet=str(s),
                            f_name=str(f.name),
                        )

                    if ctx.obj['debug']:
                        PrettyPrinter().pprint(output)

                    # output table
                    try:
                        ctx.obj['output_fcn'](output, ctx)
                    except Exception as e:
                        print(f'output {ctx.obj["output"]} failed with {e}')
                        if not ctx.obj['debug']:
                            continue
                        raise


@main.command()
@click.pass_context
@click.option(
    '--input', '-i',
    required=True,
    type=str,
    nargs=2,
    help='eparse data source',
)
@click.option(
    '--filter', '-f',
    type=str,
    nargs=2,
    multiple=True,
    help='django-style filter(s) to apply to base queryset',
)
@click.option(
    '--method', '-m',
    type=str,
    default='get_queryset',
    help='method to call on eparse model',
)
def query(ctx, input, filter, method):
    '''
    query eparse output
    '''

    ctx.obj['input_fcn'], ctx.obj['input_src'] = input
    ctx.obj['filters'] = {k: v for k, v in filter}
    ctx.obj['method'] = method

    # set input function
    try:
        m = importlib.import_module('eparse.interfaces')
        ctx.obj['input_fcn'] = getattr(m, ctx.obj['input_fcn'])

    except AttributeError as e:
        print(f'input error - there is no {ctx.obj["input_fcn"]}')
        if ctx.obj['debug']:
            raise(e)
        sys.exit(1)

    if ctx.obj['debug']:
        PrettyPrinter().pprint(ctx.obj)

    # get model from input factory
    model = ctx.obj['input_fcn'](ctx.obj['input_src'])

    # call model method and output results
    m = getattr(model, method, None)
    kwargs = ctx.obj['filters']

    # if no explicit method is available, try get_column
    if m is None:
        patt = r'^(?:get_)?(.*)$'
        m = model.get_column
        kwargs['column'] = re.match(patt, method)[1]

    # call query method
    try:
        data = m(**kwargs)
    except Exception as e:
        print(f'an error occurred: {e}')
        if ctx.obj['debug']:
            raise
        sys.exit(1)

    # output data
    try:
        ctx.obj['output_fcn'](data, ctx)
    except Exception as e:
        print(f'output {ctx.obj["output"]} failed with {e}')
        if ctx.obj['debug']:
            raise
        sys.exit(1)


def entry_point():
    '''
    required to make setuptools and click play nicely (context object)
    '''

    return sys.exit(main(obj={}))


if __name__ == '__main__':
    entry_point()
