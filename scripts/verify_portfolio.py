"""Smoke-test installed entry points using synthetic data in a temporary directory."""
import csv
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from openpyxl import Workbook


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        executable_dir = Path(sys.executable).parent
        suffix = '.exe' if os.name == 'nt' else ''

        def run(tool, *args, expected=0):
            result = subprocess.run(
                [str(executable_dir / (tool + suffix)), *args], cwd=root,
                capture_output=True, encoding='utf-8', check=False, stdin=subprocess.DEVNULL, timeout=30,
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
            )
            assert result.returncode == expected, (tool, result.returncode, result.stderr)
            return result

        book = Workbook()
        book.active.append(['id', 'name'])
        book.active.append([1, 'Alice'])
        book.active.append([2, '李明'])
        book.save(root / 'input.xlsx')
        converted = run('in2csv', 'input.xlsx').stdout
        assert list(csv.reader(io.StringIO(converted))) == [['id', 'name'], ['1', 'Alice'], ['2', '李明']]
        (root / 'input.csv').write_text(converted, encoding='utf-8')
        assert run('csvclean', '-a', 'input.csv').stderr == ''
        run('csvsql', '--db', 'sqlite:///data.db', '--insert', '--no-inference',
            '--tables', 'people', 'input.csv')
        output = run('sql2csv', '--db', 'sqlite:///data.db', '--query',
                     'SELECT id, name FROM people ORDER BY id').stdout
        assert list(csv.reader(io.StringIO(output))) == list(csv.reader(io.StringIO(converted)))
        (root / 'bad.csv').write_text('id,name\n3\n', encoding='utf-8')
        result = run('csvclean', '--length-mismatch', '--error-format', 'jsonl', 'bad.csv', expected=1)
        assert json.loads(result.stderr)['row'] == ['3']
        print('PASS: Excel -> CSV -> validation -> SQLite -> CSV; JSONL error report')


if __name__ == '__main__':
    main()
