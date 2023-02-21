# gitbi

_Gitbi_ is a lightweight business intelligence application that reads configuration from a git repository. This design enables you to write and commit SQL queries and visualizations ([vega-lite](https://github.com/vega/vega-lite) specs) directly to git repo and have _Gitbi_ display them. Of course, if you wish to edit them via web interface, that's also possible.

Test it now with sample db and config:

```
docker run -p 8000:8000 pieca/gitbi:0.5
```

See full deployment example: [ppatrzyk/gitbi-example](https://github.com/ppatrzyk/gitbi-example).

## Configuration

_Gitbi_ requires the following to run:

### Repository with saved queries

Repository needs to have the following structure:
- directories in repo root refer to databases
- files in each directory are queries/visualizations to be run against respective database
    - files ending with `.sql` are queries
    - files `<query_file_name>.json` are read as [vega-lite](https://github.com/vega/vega-lite) specs[^1]
- README.md file content will be displayed on _Gitbi_ main page

[^1]: You should pass Vega-Lite [specification](https://vega.github.io/vega-lite/docs/spec.html) without `data` field. Data will be appended automatically by gitbi based on query result.

### Environment variables

Name | Description
--- | ---
GITBI\_REPO\_DIR | Path to the repository
GITBI\_<DB\_NAME>\_CONN | Connection string
GITBI\_<DB\_NAME>\_TYPE | Database type (see below for permissible values)
GITBI\_AUTH | (Optional) List of users (`"user1:password1, user2:password2"`), if set, Basic HTTP Auth (RFC 7617) required for all calls
GITBI\_SMTP\_USER | (Optional) SMTP user
GITBI\_SMTP\_PASS | (Optional) SMTP password
GITBI\_SMTP\_URL | (Optional) SMTP server (`"smtp.example.com:587"`)
GITBI\_SMTP\_EMAIL | (Optional) SMTP email to send from

Following database types are supported:

Type (value of GITBI\_<DB\_NAME>\_TYPE) | Connection string format (GITBI\_<DB\_NAME>\_CONN)
--- | ---
clickhouse | clickhouse://[login]:[password]@[host]:[port]/[database]
postgres | postgresql://[userspec@][hostspec][/dbname][?paramspec]
sqlite | path to db file

### Example

Assume you have repository with the following structure:

```
repo
├── db1
│   ├── query1.sql
│   ├── query2.sql
│   └── query2.sql.json
├── db2
│   ├── query3.sql
│   ├── query3.sql.json
│   ├── query4.sql
│   └── query5.sql
└── README.md
```

There are 2 databases named _db1_ and _db2_. _db1_ has 2 queries, one of them has also visualization; _db2_ has 3 queries, 1 with added visualization.

For configuration you'd need to set the following environment variables:

```
GITBI_REPO_DIR=<path_to_repo>
GITBI_DB1_CONN=<conn_str_to_db1>
GITBI_DB1_TYPE=<type_db1>
GITBI_DB2_CONN=<conn_str_to_db2>
GITBI_DB2_TYPE=<type_db2>
```

## Usage

You can view your queries with two endpoints:

- `/query/{db}/{file}/{state}`: this endpoint displays query on a web page and allows you to edit or execute it interactively
- `/report/{db}/{file}/{state}`: this endpoint displays _and executes_ query, returning self-contained and non-interactive (no JS) html with results

The use case for using report is to execute it and pipe results directly to email for reporting and alerting. Examples how to do it are auto-generated on each query page.

Alternatively, for reporting and alerting, you can set up email credentials in _Gitbi_ and have the app email it to you. Relevant routes are:

- `/email/alert/{db}/{file}/{state}?to=your@email.com`
- `/email/report/{db}/{file}/{state}to=your@email.com`

Both routes require query parameter `to` to be set. The difference between aforementioned routes is that _report_ always sends an email with results when invoked, while _alert_ sends results _only if there are some rows returned_. Write your alert queries in a way that they usually do not return anything, but you want to be notified when they do. If you don't have email credentials set up, you can implement this logic yourself - the number of rows for a query is available in a header `Gitbi-Row-Count`.

Note, _Gitbi_ does not attempt to reinvent the wheel and suggests to use e.g. CRON for scheduling.

## Repo setup

The easiest way to run _Gitbi_ is to set up a repository at the same server the app is running, and then sync changes into your local repo via ssh. This requires setting proper permissions for everything to work smoothly. Example setup:

```
# initialize as shared repo
# the command below allows any user in group <GROUP> to push into repo, for other options see https://git-scm.com/docs/git-init
git init --shared=group <REPO_NAME>
chgrp -R <GROUP> <REPO_NAME>
chmod g+rwxs <REPO_NAME>
# enable pushing to checked out branch
git config receive.denyCurrentBranch updateInstead
```

## Development

```
# run local
GITBI_REPO_DIR="./tests/gitbi-testing" GITBI_SQLITE_CONN="$(realpath ./tests/gitbi-testing/db.sqlite)" GITBI_SQLITE_TYPE=sqlite ./start_app.sh

# build image
docker build -t pieca/gitbi:<version> .
```

## Some alternatives

- if you want to generate static html reports from db queries using Python: [merkury](https://github.com/ppatrzyk/merkury)
- if you want to analyze single sqlite db: [datasette](https://github.com/simonw/datasette)
- if you want to run queries from your browser: [sqlpad](https://github.com/sqlpad/sqlpad), [chartbrew](https://github.com/chartbrew/chartbrew)
- if you want a full-blown BI solution: [metabase](https://github.com/metabase/metabase)

## Acknowledgements

Backend:
- [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver)
- [jinja](https://github.com/pallets/jinja/)
- [markdown](https://github.com/Python-Markdown/markdown)
- [psycopg](https://github.com/psycopg/psycopg)
- [pygit2](https://github.com/libgit2/pygit2)
- [sqlparse](https://github.com/andialbrecht/sqlparse)
- [starlette](https://github.com/encode/starlette)
- [uvicorn](https://github.com/encode/uvicorn)

Frontend:
- [codejar](https://github.com/antonmedv/codejar)
- [Font Awesome](https://iconscout.com/contributors/font-awesome)
- [highlight](https://github.com/highlightjs/highlight.js)
- [htmx](https://github.com/bigskysoftware/htmx)
- [pico](https://github.com/picocss/pico)
- [simple-datatables](https://github.com/fiduswriter/simple-datatables)
- [ubuntu font](https://ubuntu.com/legal/font-licence)
- [vega](https://github.com/vega)
