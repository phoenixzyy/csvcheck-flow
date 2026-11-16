# Portfolio progress

## csvcheck-flow implementation — 2026-11-16

Scope: one selected Python data-automation project, csvkit. The existing
workspace-wide progress file was read and appended without replacing its
earlier records. This repository contains only the current project checkpoint.

- Verified GitHub connector: phoenixzyy, ID 7067843. No lsbjason identity used.
- Proposed normal Fork name: `phoenixzyy/csvcheck-flow`, from wireservice/csvkit.
  No remote Fork exists from this work; no push, remote commit or CI run claimed.
- Local full-history clone; fixed upstream baseline
  `43d09bf1f39382bc2d66c4f892c9814901179ff8`. Origin still points to upstream.
- Read existing progress before appending. Workspace `.agents` is empty; no
  repository AGENTS.md/SKILL.md was found. Read upstream contribution guidance.
- MIT `COPYING` copyright (2016 Christopher Groskopf and contributors) and
  `AUTHORS.rst` retained unchanged. Reviewed csvclean, RowChecker, csvsql and tests.
- Reviewed recent related PRs #1339, #1363, #1383, #1378, #1257. Avoided their
  proposed changes. The existing CSV error report was already machine-readable.
- Implemented one bounded extension: `csvclean --error-format jsonl`, with default
  CSV preserved. Separate header/value arrays preserve ragged rows and duplicate
  headers; optional labels and escaped Unicode/multiline values are supported.
- Added 13 subprocess contract cases. Red on original production code: 13 failed
  (new option unsupported). Focused csvclean + JSONL + csvsql: 62 passed, 1 skipped,
  12 subtests passed. Baseline: 367 passed, 4 skipped, 31 subtests passed. Final:
  380 passed, 4 skipped, 31 subtests passed. Both full runs emitted 35 warnings.
- Linux / Python 3.12.14 / agate 1.14.2 / agate-sql 0.7.3 / SQLAlchemy 2.1.8 /
  openpyxl 3.1.5 / pytest 9.2.0. flake8, isort and git diff --check passed.
- Built wheel and sdist. Installed wheel in a separate virtual environment and
  ran the installed entry points outside the source directory: synthetic Excel
  -> CSV -> validation -> SQLite -> CSV and JSONL error report all passed.
  Build emitted setuptools packaging/deprecation warnings; no build failure.
- Added PORTFOLIO.md, LEARNING.zh-CN.md, updated CLI docs/man page and README.
  No claims of independent authorship, upstream endorsement or invented expertise.
- CI prepared for Ubuntu Python 3.10/3.12/3.14, full tests and synthetic smoke.
  Upstream Docker/PyPI publishing, coverage upload and auto-merge are guarded
  to upstream only. No deployment, online service or paid resource was created.
- Limits: JSONL formats check reports only, not all fatal diagnostics; checker
  error buffering and line-number semantics remain upstream. No SQL transaction
  bug claimed or fixed. Other platforms/Python versions, PostgreSQL/MySQL,
  performance and remote CI remain unverified.
- Evidence logs: csvkit-install.log, csvkit-baseline.log, csvkit-red.log,
  csvkit-focused.log, csvkit-final.log, csvkit-smoke.log, csvkit-lint.log,
  csvkit-build.log, csvkit-wheel-install.log, csvkit-wheel-smoke.log.
- Publication blocker: GitHub connector exposes no Fork operation; `gh api user`
  reports no CLI authentication, and browser explicitly says sign-in is required
  to Fork. Normal Fork creation needs an authenticated phoenixzyy session. No
  repository was created by another route or account. No upstream contact/Issue/PR.

Next: authenticate phoenixzyy for normal Fork creation, choose `csvcheck-flow`,
verify owner ID and parent relationship, push the reviewed commit without force,
then verify the remote SHA and CI. Do not create any other candidate or deploy.

Final local checks: check-manifest confirmed version-control and sdist file lists match; installed CLI smoke rerun passed. No remote action has occurred.
