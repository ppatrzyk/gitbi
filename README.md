# Gitbi

_Gitbi_ is a lightweight BI web app that uses git repository as a source of saved queries, visualizations and dashboards. Everything is stored as text files which can be easily accessed and edited outside of the app (in addition to using web interface).

Features:

- You can write queries using either SQL or [PRQL](https://github.com/PRQL/prql)
- Interactive visualizations with [ECharts](https://github.com/apache/echarts)
- Scheduling reports and alerts
- Currently supported DBs: clickhouse, duckdb (query csv files), postgresql, sqlite

Test it now with sample dbs and config:

```
docker run -p 8000:8000 pieca/gitbi:latest
```

Or view [screenshots](screenshots.md).

See full deployment example: [ppatrzyk/gitbi-example](https://github.com/ppatrzyk/gitbi-example).

## Configuration

_Gitbi_ requires the following to run:

### Config repository

Repository needs to have the following structure:
- directories in repo root refer to databases
- files in each directory are queries/visualizations to be run against respective database
    - files with `.sql` or `.prql` extension are queries
    - (optional) files with `.json` extension are saved visualizations
- (optional) special directory `_dashboards` that contains dashboard specifications (`.json` format)
- (optional) special file `schedule.json` that contains scheduled reports and alerts
- (optional) README.md file content will be displayed on _Gitbi_ main page

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
clickhouse | `clickhouse://[login]:[password]@[host]:[port]/[database]`
duckdb | path to db file (or `:memory:`)
postgres | `postgresql://[userspec@][hostspec][/dbname][?paramspec]`
sqlite | path to db file (or `:memory:`)

### Example

Assume you have repository with the following structure:

```
repo
├── _dashboards
│   └── my_dashboard.json
├── db1
│   ├── query1.sql
│   ├── query2.sql
│   └── query2.sql.json
├── db2
│   ├── query3.sql
│   ├── query3.sql.json
│   ├── query4.sql
│   └── query5.sql
├── README.md
└── schedule.json
```

There are 2 databases named _db1_ and _db2_. _db1_ has 2 queries, one of them has also visualization; _db2_ has 3 queries, 1 with added visualization. There is also one dashboard called _my_dashboard.json_.

For configuration you'd need to set the following environment variables:

```
GITBI_REPO_DIR=<path_to_repo>
GITBI_DB1_CONN=<conn_str_to_db1>
GITBI_DB1_TYPE=<type_db1>
GITBI_DB2_CONN=<conn_str_to_db2>
GITBI_DB2_TYPE=<type_db2>
```

## Config formatting

### Visualization

Visualization is a JSON file with the following format:

```
{
  "type": "scatter|line|bar|heatmap",
  "xaxis": <column_name>,
  "yaxis": <column_name>,
  "zaxis": <column_name>,
  "group": <column_name>
}
```

### Dashboard

Dashboard is a JSON file with the following format, list can have any number of entries:

```
[
  [
    "<db_name>",
    "<query_file_name>"
  ],
  [
    "<db_name>",
    "<query_file_name>"
  ],
  ...
]
```

### Scheduler

Format for `schedule.json` file, list can have any number of entries:

```
[
  {
    "cron": "<cron_expression>",
    "db": "<db_name>",
    "file": "<query_file_name>",
    "type": "alert|report",
    "format": "html|text|csv|json",
    "to": "<email_address>"
  },
  ...
]
```

Notes:

- _report_ always sends an email with results when invoked, while _alert_ sends results only if there are some rows returned. Write your alert queries in a way that they usually do not return anything, but you want to be notified when they do
- any changes in scheduler require restarting the app for changes to be reflected

### System CRON examples

If you don't want to setup email credentials in _Gitbi_, you can still just use CRON to to generate reports on schedule. Examples:

```
# HTML report via sendmail
* * * * * echo -e "Subject: Gitbi report\nContent-Type: text/html\n\n$(curl -s -u <user>:<password> <report_url>)" | /usr/sbin/sendmail -f <sender_email> <recipient_email>

# HTML report via mailgun api
* * * * * curl -X POST --user "api:<mailgun_api_key>" --data-urlencode from=<sender_email> --data-urlencode to=<recipient_email> --data-urlencode subject="Gitbi report" --data-urlencode html="$(curl -s -u <user>:<password> <report_url>)" https://api.eu.mailgun.net/v3/SENDER_DOMAIN/messages
```

You can copy `report_url` from every query page. You could even implement alerting logic yourself with `/report` endpoint - the number of rows for a query is available in a header `Gitbi-Row-Count`.

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
# install dependencies
pip3 install -r requirements.txt

# run with sample repo
./start_app.sh

# run with testing repo
GITBI_REPO_DIR="./tests/gitbi-testing" GITBI_SQLITE_CONN="$(realpath ./tests/gitbi-testing/db.sqlite)" GITBI_SQLITE_TYPE=sqlite ./start_app.sh

# build image
docker build -t pieca/gitbi:<version> .
```

## Some alternatives

- generate static html reports using Python: [merkury](https://github.com/ppatrzyk/merkury)
- create custom dashboards using SQL and markdown: [evidence](https://github.com/evidence-dev/evidence)
- analyze single sqlite db: [datasette](https://github.com/simonw/datasette)
- run SQL queries from your browser: [sqlpad](https://github.com/sqlpad/sqlpad)
- full-blown BI solution: [metabase](https://github.com/metabase/metabase)

## Acknowledgements

Backend:
- [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver)
- [duckdb](https://github.com/duckdb/duckdb/tree/master/tools/pythonpkg)
- [jinja](https://github.com/pallets/jinja/)
- [markdown](https://github.com/Python-Markdown/markdown)
- [prettytable](https://github.com/jazzband/prettytable)
- [prql](https://github.com/PRQL/prql/tree/main/bindings/prql-python)
- [psycopg](https://github.com/psycopg/psycopg)
- [pygit2](https://github.com/libgit2/pygit2)
- [sqlparse](https://github.com/andialbrecht/sqlparse)
- [starlette](https://github.com/encode/starlette)
- [uvicorn](https://github.com/encode/uvicorn)

Frontend:
- [codejar](https://github.com/antonmedv/codejar)
- [ECharts](https://github.com/apache/echarts)
- [Font Awesome](https://iconscout.com/contributors/font-awesome)
- [highlight](https://github.com/highlightjs/highlight.js)
- [htmx](https://github.com/bigskysoftware/htmx)
- [pure.css](https://github.com/pure-css/pure)
- [simple-datatables](https://github.com/fiduswriter/simple-datatables)
- [ubuntu font](https://ubuntu.com/legal/font-licence)
