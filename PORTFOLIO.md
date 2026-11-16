# csvcheck-flow — proposed portfolio fork

Publication is pending authentication. No remote fork has been created, no commit
has been pushed, and remote CI has not run. The proposed GitHub repository name
is `csvcheck-flow` under the verified account `phoenixzyy` (ID 7067843).

## Origin and actual contribution

This project derives from [wireservice/csvkit](https://github.com/wireservice/csvkit),
fixed at `43d09bf1f39382bc2d66c4f892c9814901179ff8` for this review on 2026-11-16.
The full upstream Git history is retained locally. Normal GitHub Fork creation,
with that upstream relationship, is required before publication.

The CSV/Excel conversion, cleaning engine, SQL import and CLI framework are
upstream work. `COPYING` retains the MIT license and copyright (2016 Christopher
Groskopf and contributors); `AUTHORS.rst` is unchanged. This is not a claim to
have created csvkit or to have upstream endorsement. The extension was prepared
and tested with Codex assistance for this portfolio; independent human review
has not occurred. No professional experience or proficiency is inferred from it.

The actual production change is **opt-in `csvclean --error-format jsonl`**.
The default report was already machine-readable CSV. It can be ragged when an
input row has too few or too many fields; headers can also be duplicate or empty.
The new report makes the boundaries explicit with separate `column_names` and
`row` arrays. It adds one serialization branch without changing `RowChecker`,
cleaned CSV output, checks, repairs, or check-error exit status 1.

Each JSON object has integer `line_number`, string `msg`, arrays `column_names`
and `row`, and an optional string `label`. JSON escaping keeps each record on one
physical line, including Unicode and embedded-newline input. Empty/header-only
or valid input produces no report. `--error-format csv` explicitly selects the
unchanged default. `--label -` keeps upstream filename/stdin semantics.

Related work reviewed: [#1339](https://github.com/wireservice/csvkit/pull/1339)
(empty-column removal, already in baseline),
[#1363](https://github.com/wireservice/csvkit/pull/1363) (structured empty-column
indices, a different proposal), [#1383](https://github.com/wireservice/csvkit/pull/1383)
(empty-first-row join), [#1378](https://github.com/wireservice/csvkit/pull/1378)
(engine-option parsing), and [#1257](https://github.com/wireservice/csvkit/pull/1257)
(SQL delimiter). No patches from these PRs were copied. Search is not proof that
no similar proposal exists. No upstream issues, PRs or messages were created.

`csvsql.py` and its tests were reviewed: it already begins a transaction, commits
after queries, and closes connections in `finally`. No transaction defect is
claimed or repaired here. The smoke test verifies a successful SQLite import,
not rollback semantics or atomic DDL on all databases.

## Reproduce

```sh
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest -q
python scripts/verify_portfolio.py
csvclean --length-mismatch --error-format jsonl examples/bad.csv > cleaned.csv 2> errors.jsonl
# The preceding fixture intentionally exits 1.
python -c 'import json; print([json.loads(line)["row"] for line in open("errors.jsonl")])'
```

On Windows activate `.venv\Scripts\activate` instead. The smoke script uses only
synthetic records in a temporary directory and installed entry points. It creates
no server and contacts no database service. SQLite is a local temporary file.

For a direct red/green comparison, create a temporary checkout of the baseline,
copy only `tests/test_utilities/test_csvclean_jsonl.py` into it, install its test
dependencies and run that file: the 13 cases fail because the option is absent.
Run the same file on this change: 13 cases pass. This is an extension test,
not a claim of 13 upstream bugs.

## Verification and limits

Local verification: Linux, Python 3.12.14; agate 1.14.2, agate-sql 0.7.3,
SQLAlchemy 2.1.8, openpyxl 3.1.5, pytest 9.2.0.

| Check | Result |
| --- | --- |
| Unchanged baseline | 367 passed, 4 skipped, 31 subtests passed |
| New contract tests on unchanged production code | 13 failed (unsupported option) |
| Focused csvclean + JSONL + csvsql | 62 passed, 1 skipped, 12 subtests passed |
| Complete modified suite | 380 passed, 4 skipped, 31 subtests passed |
| Baseline and final warnings | 35 each; no new warning count |
| Installed CLI smoke | Excel → CSV → validation → SQLite → CSV, plus JSONL: passed |
| flake8 and isort, csvkit/tests/scripts | Passed |
| Build and clean wheel installation | Passed; setuptools packaging/deprecation warnings |
| Installed wheel smoke outside source directory | Passed |
| check-manifest | Version-control and sdist file lists match |

Build/wheel results and publication status are recorded in `PORTFOLIO_PROGRESS.md`.
Logs remain in the parent workspace as `csvkit-*.log`.

JSONL encodes **check reports only**, not argument/parser/decoding/I/O errors.
Such failures can put non-JSON diagnostics on stderr. Error buffering and memory
cost remain upstream behavior; this is not a streaming-memory improvement.
Line numbers keep the existing reader-ending-physical-line-minus-one semantics
after skip handling, not a newly defined record index. Empty-column findings keep
upstream synthetic line 1. The report reflects checker headers/errors before
output-only column removal; header normalization still applies. No machine-stable
error codes or structured empty-column indices are introduced.

Only local Linux/Python 3.12 results are verified. Windows/macOS, other Python
versions, PostgreSQL/MySQL, large-file throughput and remote CI are unverified.
This version retains the upstream distribution name/version for local testing;
it must not be published to PyPI as a new upstream release.

CI retains upstream tests and stdin/pipe checks, adds the synthetic smoke flow,
and narrows the portfolio matrix to Ubuntu with Python 3.10/3.12/3.14. Coverage
upload, Docker publishing, PyPI publishing and auto-merge are guarded for the
upstream repository only. No deployment or online service is part of this work.

## Suggested review

Read the production diff first, then the 13 subprocess cases covering ragged rows,
duplicate/empty headers, Unicode/multiline text, labels, empty input, empty-column
removal, repairs/omission, default compatibility and invalid formats. Review
privacy before using real CSV input: both report formats include erroneous cell
values. The included examples and smoke data are synthetic.
