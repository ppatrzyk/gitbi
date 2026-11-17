# Gitbi

_Gitbi_ is a lightweight BI web app that uses config files as a source of saved queries, visualizations and dashboards.

Features:

- You can write queries using either SQL or [PRQL](https://github.com/PRQL/prql)
- Interactive visualizations with [ECharts](https://github.com/apache/echarts)
- Mailing reports and alerts
- Currently supported DBs: clickhouse, duckdb (query csv files), postgresql, sqlite

```bash
podman run \
  -p 8000:8000 \
  -v ./example:/gitbi/example \
  -e GITBI_CONFIG_DIR=./example \
  -e GITBI_POKEMON_TYPE=sqlite \
  -e GITBI_POKEMON_CONN=./example/pokemon.sqlite \
  -e GITBI_SHOOTINGS_TYPE=duckdb \
  -e GITBI_SHOOTINGS_CONN=":memory:" \
  -e GITBI_SUICIDE_TYPE=sqlite \
  -e GITBI_SUICIDE_CONN=./example/suicide.sqlite \
  ghcr.io/ppatrzyk/gitbi:v0.11
```

Or view [screenshots](screenshots.md).

## Configuration

_Gitbi_ requires the following to run:

### Configuration directory

Directory needs to have the following structure:
- directories in repo root refer to databases
- files in each directory are queries/visualizations to be run against respective database
    - files with `.sql` or `.prql` extension are queries
    - (optional) files with `.json` extension are saved visualizations
- (optional) special directory `_dashboards` that contains dashboard specifications (`.json` format)
- (optional) README.md file content will be displayed on _Gitbi_ main page

### Environment variables

Name | Description
--- | ---
GITBI\_CONFIG\_DIR | Path to configuration directory
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

Assume you have directory with the following structure:

```bash
repo
├── _dashboards
│   └── my_dashboard.json
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

There are 2 databases named _db1_ and _db2_. _db1_ has 2 queries, one of them has also visualization; _db2_ has 3 queries, 1 with added visualization. There is also one dashboard called _my_dashboard.json_.

For configuration you'd need to set the following environment variables:

```bash
GITBI_CONFIG_DIR=<path_to_repo>
GITBI_DB1_CONN=<conn_str_to_db1>
GITBI_DB1_TYPE=<type_db1>
GITBI_DB2_CONN=<conn_str_to_db2>
GITBI_DB2_TYPE=<type_db2>
```

## Config formatting

### Visualization

Visualization is a JSON file with the following format:

```json
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

```json
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

### Reporting

For every query, you have a _report_ endpoint that provides query results in html and text formats, as well as data only csv and json. This endpoint accepts two optional query parameters:

- `mail`: if this is not empty, gitbi will send an email with the result to specified address
- `alert`: if this is not empty, gitbi will send results via email only if there are some rows returned. Write your alert queries in a way that they usually do not return anything, but you want to be notified when they do. This parameter makes sense only together with email.

Scheduling is possible via any external service, most commonly CRON. Example:

```bash
# Report sent at 6am
0 6 * * * curl -s -u <user>:<password> <report_url>?mail=<your_email>

# Alert checked every minute
* * * * * curl -s -u <user>:<password> <report_url>?alert=true&mail=<your_email>
```

If you don't want to setup email credentials in _Gitbi_, you can still use CRON to to send reports with other tools. Examples:

```bash
# HTML report via sendmail
* * * * * echo -e "Subject: Gitbi report\nContent-Type: text/html\n\n$(curl -s -u <user>:<password> <report_url>)" | /usr/sbin/sendmail -f <sender_email> <recipient_email>

# HTML report via mailgun api
* * * * * curl -X POST --user "api:<mailgun_api_key>" --data-urlencode from=<sender_email> --data-urlencode to=<recipient_email> --data-urlencode subject="Gitbi report" --data-urlencode html="$(curl -s -u <user>:<password> <report_url>)" https://api.eu.mailgun.net/v3/SENDER_DOMAIN/messages
```

You can copy `report_url` from every query page.

## Development

```bash
# prod
pip3 install -r requirements.txt
pip3 install clickhouse-driver duckdb Jinja2 Markdown prettytable prql-python psycopg psycopg-binary sqlparse starlette python-multipart uvicorn

# dev
pip3 install -r requirements-dev.txt
pip3 install httpx2 pytest ruff

# run with example repo
GITBI_CONFIG_DIR=./example \
GITBI_POKEMON_TYPE=sqlite \
GITBI_POKEMON_CONN=./example/pokemon.sqlite \
GITBI_SHOOTINGS_TYPE=duckdb \
GITBI_SHOOTINGS_CONN=":memory:" \
GITBI_SUICIDE_TYPE=sqlite \
GITBI_SUICIDE_CONN=./example/suicide.sqlite \
uvicorn --log-level=debug --app-dir=app main:app

# run with testing repo
GITBI_CONFIG_DIR=./tests \
GITBI_SQLITE_TYPE=sqlite \
GITBI_SQLITE_CONN=./tests/gitbi-testing/db.sqlite \
uvicorn --log-level=debug --app-dir=app main:app

# build image
podman build -t ghcr.io/ppatrzyk/gitbi:dev .
```
