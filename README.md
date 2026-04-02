# Jira-PoC
EDIT: Apr-2026, just added a README.md

A small proof of concept built to extract operational metrics from Jira projects and export them into CSV files for further analysis in Excel.

This repository reflects an internal tool I put together to answer a practical need: get a quick view of project progress, Story Point consumption, and hours spent without depending on heavyweight reporting dashboards. The focus was always utility over polish.

## What This Project Does

The scripts in this repository connect to a Jira server, retrieve issues for one or more projects, and generate CSV exports with delivery and effort data such as:

- total Story Points
- completed Story Points
- in-progress Story Points
- hours spent
- issue-level export data
- sprint participation counts
- issue grouping by Epic

The generated files were intended to be consumed mainly from Excel for ad hoc reporting and project follow-up.

## Main Scripts

### `get_SPs.py`

Simple project-level Story Point extraction.

It connects to Jira, retrieves all issues for a project, filters relevant issue types, and calculates:

- completed development Story Points
- completed analysis/testing Story Points
- total Story Points
- issue-level CSV export

If no project key is passed, it defaults to `BSTI`.

Example:

```bash
python get_SPs.py BSTI
```

### `get_SP_HH_by_EPIC.py`

More complete report including Story Points, spent hours, sprint count, creation date, and Epic association.

This script produces:

- a detailed CSV export with issue metadata
- a summary CSV with aggregated metrics

Example:

```bash
python get_SP_HH_by_EPIC.py BSTI your_user your_password
```

### `src/backend/BackEnd.py`

A first pass at modularizing the original scripts into reusable classes.

It includes helpers to:

- load configuration from `properties.ini`
- connect to Jira
- iterate across a configured list of monitored projects
- export Jira structural data such as projects, fields, and sprints
- generate project progress and cost summaries

This file should be read as an internal refactor effort rather than a finished framework.

## Configuration

The repository expects a `properties.ini` file with Jira connection settings and the list of monitored projects.

Expected structure:

```ini
[credentials]
user=your_user
pwd=your_password

[server]
url=http://your-jira-server

[monitor]
projects=PROJ1,PROJ2,PROJ3
```

## Output

The scripts write timestamped CSV files intended for spreadsheet consumption, typically under an `xls-export` folder.

Typical outputs include:

- issue-level export files
- process summary files
- field/code reference dumps

## Technical Context

This project was written in a Python 2 environment and reflects the conventions and constraints of that period.

Notable characteristics:

- Python 2 style modules such as `cStringIO` and `ConfigParser`
- legacy encoding handling through `sys.setdefaultencoding`
- direct use of the `jira` Python library
- local bundled virtual environment artifacts in `jira_python`

## Current Status

This repository is best understood as a historical proof of concept.

It was useful internally for quick Jira metric extraction, but it was not evolved into a production-grade application. If you plan to reuse it today, expect to modernize several parts:

- migrate to Python 3
- externalize and secure credentials
- replace hardcoded custom field IDs with configurable mappings
- improve error handling and logging
- separate reusable logic from executable scripts
- make export paths platform-independent

## Known Limitations

- strongly tied to a specific Jira instance and field layout
- relies on custom Jira field IDs such as Story Points, Epic Link, and Sprint
- assumes issue types and workflow statuses that may not exist in other Jira setups
- uses Windows-style paths in several places
- includes prototype and partially unrelated code in the modularized backend

## Why This Exists

The intent behind this project was straightforward: turn Jira issue data into something immediately usable by project teams and managers, with minimal ceremony.

Sometimes a lightweight script answers the business question faster than a bigger system. This repository came out of that mindset.

## Repository Notes

If you are browsing this project from GitHub, keep in mind that the repository captures the original PoC as it was used internally. It is intentionally preserved in a fairly raw form rather than rewritten to look more modern than it really is.

That said, the core idea remains valid: extract structured Jira data, compute practical delivery metrics, and export them into simple files anyone can inspect.

## License

No license has been added to this repository yet.
