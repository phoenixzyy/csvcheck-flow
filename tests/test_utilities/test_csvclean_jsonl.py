"""Exercise the installed CLI contract, including separate stdout/stderr streams."""
import csv
import io
import json
import subprocess
import sys

import pytest


def clean(data, *args):
    return subprocess.run(
        [sys.executable, '-m', 'csvkit.utilities.csvclean', *args],
        input=data, capture_output=True, encoding='utf-8', check=False,
    )


def records(result):
    assert result.returncode == 1
    return [json.loads(line) for line in result.stderr.splitlines()]


def test_jsonl_preserves_ragged_rows_and_duplicate_headers():
    data = 'name,name,\nshort\nlong,2,3,extra\n'
    result = clean(data, '--length-mismatch', '--error-format', 'jsonl')
    assert result.stdout == data
    assert records(result) == [
        {'line_number': 1, 'msg': 'Expected 3 columns, found 1 columns',
         'column_names': ['name', 'name', ''], 'row': ['short']},
        {'line_number': 2, 'msg': 'Expected 3 columns, found 4 columns',
         'column_names': ['name', 'name', ''], 'row': ['long', '2', '3', 'extra']},
    ]


def test_jsonl_unicode_multiline_and_label():
    result = clean('a,b\n"你好\nworld"\n', '--length-mismatch', '--error-format', 'jsonl', '--label', '批次\n1')
    assert len(result.stderr.splitlines()) == 1
    assert records(result) == [
        {'line_number': 2, 'msg': 'Expected 2 columns, found 1 columns',
         'column_names': ['a', 'b'], 'row': ['你好\nworld'], 'label': '批次\n1'},
    ]


@pytest.mark.parametrize('label,expected', [('-', 'stdin'), ('batch-1', 'batch-1'), ('', None)])
def test_jsonl_stdin_label(label, expected):
    result = clean('a,b\nx\n', '--length-mismatch', '--error-format', 'jsonl', '--label', label)
    record = records(result)[0]
    if expected is None:
        assert 'label' not in record
    else:
        assert record['label'] == expected


def test_jsonl_filename_label(tmp_path):
    path = tmp_path / 'batch.csv'
    path.write_text('a,b\nx\n', encoding='utf-8')
    result = clean('', '--length-mismatch', '--error-format', 'jsonl', '--label', '-', str(path))
    assert records(result)[0]['label'] == str(path)


@pytest.mark.parametrize('data', ['', 'a,b\n', 'a,b\n1,2\n'])
def test_jsonl_no_errors_is_silent(data):
    result = clean(data, '-a', '--error-format', 'jsonl')
    assert result.returncode == 0
    assert result.stderr == ''


def test_jsonl_empty_columns_and_removed_output():
    result = clean('a,b,c\n1,,3\nx\n', '-a', '--remove-empty-columns', '--error-format', 'jsonl')
    assert result.stdout == 'a,c\n1,3\nx\n'
    errors = records(result)
    assert len(errors) == 2
    assert errors[0]['row'] == ['x']
    assert errors[1]['row'] == ['', '', '']
    assert all(error['column_names'] == ['a', 'b', 'c'] for error in errors)
    assert errors[1]['msg'] == "Empty columns named 'b'! Try: csvcut -C 2"


def test_jsonl_omit_and_fix():
    result = clean('a,b\nx\ny,z,extra\n', '--length-mismatch', '--fill-short-rows',
                   '--omit-error-rows', '--error-format', 'jsonl')
    assert result.stdout == 'a,b\nx,\n'
    assert [error['row'] for error in records(result)] == [['y', 'z', 'extra']]


def test_explicit_csv_matches_default():
    data = 'a,b\nx\ny,z,extra\n'
    default = clean(data, '--length-mismatch', '--label', 'batch')
    explicit = clean(data, '--length-mismatch', '--label', 'batch', '--error-format', 'csv')
    assert (explicit.returncode, explicit.stdout, explicit.stderr) == (
        default.returncode, default.stdout, default.stderr,
    )
    assert list(csv.reader(io.StringIO(explicit.stderr))) == [
        ['label', 'line_number', 'msg', 'a', 'b'],
        ['batch', '1', 'Expected 2 columns, found 1 columns', 'x'],
        ['batch', '2', 'Expected 2 columns, found 3 columns', 'y', 'z', 'extra'],
    ]


def test_invalid_error_format():
    result = clean('a,b\nx\n', '--length-mismatch', '--error-format', 'xml')
    assert result.returncode == 2
    assert result.stdout == ''
    assert 'invalid choice' in result.stderr
