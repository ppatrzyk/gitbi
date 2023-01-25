# gitbi

**[DEVELOPMENT IN PROGRESS]**

_Gitbi_ is a lightweight business intelligence application that reads all queries from a git repository. This design enables you to write and commit SQL queries directly to git repo and have _Gitbi_ display them.

## Configuration

_Gitbi_ requires the following to run:

### Repository with saved queries

Repository needs to have the following structure:
- directories in repo root refer to databases
- files in each directory are queries to be run against respective database
- README.md file content will be displayed on _Gitbi_ main page

### Environment variables

Name | Description
--- | ---
GITBI\_REPO\_DIR | Path to the repository
GITBI\_<DB\_NAME>\_CONN | Connection string
GITBI\_<DB\_NAME>\_TYPE | Database type (see below for permissible values)

Following database types are supported:

Type (value of GITBI\_<DB\_NAME>\_TYPE) | Connection string format (GITBI\_<DB\_NAME>\_CONN)
--- | ---
clickhouse | clickhouse://[login]:[password]@[host]:[port]/[database]
postgres | postgresql://[userspec@][hostspec][/dbname][?paramspec]
sqlite | path to db file

### Example

Assume you have repository with the following structure:

```
repo/
├── db1
│   ├── query1.sql
│   └── query2.sql
├── db2
│   ├── query3.sql
│   ├── query4.sql
│   └── query5.sql
└── README.md
```

There are 2 databases named _db1_ and _db2_. For configuration you'd need to set the following environment variables:

```
GITBI_REPO_DIR=<path_to_repo>
GITBI_DB1_CONN=<conn_str_to_db1>
GITBI_DB1_TYPE=<type_db1>
GITBI_DB2_CONN=<conn_str_to_db2>
GITBI_DB2_TYPE=<type_db2>
```

For a working deployment example, see https://github.com/ppatrzyk/gitbi-example

## Development

```
# run local
GITBI_REPO_DIR="./tests/gitbi-testing" ./start_app.sh

# build image
docker build -t pieca/gitbi:<version> .
```

## Alternatives

- if you want to generate static html reports from db queries using Python: [merkury](https://github.com/ppatrzyk/merkury)
- if you want to analyze single sqlite db: [datasette](https://github.com/simonw/datasette)

## Acknowledgements

Backend:
- [pygit2](https://github.com/libgit2/pygit2)
- [starlette](https://github.com/encode/starlette)

Frontend:
- [codejar](https://github.com/antonmedv/codejar)
- [highlight](https://github.com/highlightjs/highlight.js)
- [htmx](https://github.com/bigskysoftware/htmx)
- [pico](https://github.com/picocss/pico)
- [simple-datatables](https://github.com/fiduswriter/simple-datatables)
- [vega](https://github.com/vega)
