# gitbi

[In Progress]

_Gitbi_ is a lightweight business intelligence application that reads all data from a git repository. This design enables you to write and commit SQL queries directly to git repo and have _Gitbi_ display them.

## Configuration

_Gitbi_ requires the following to run

### Repository with saved queries

Repository needs to have the following structure:
- directories in repo root refer to databases
- files in each directory are queries to be run against respective database
- README.md file content will be displayed on _Gitbi_ main page

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

### Environment variables

Name | Description
--- | ---
GITBI_REPO_DIR | Path to the repository
GITBI_<DB_NAME>_CONN | Connection string
GITBI_<DB_NAME>_TYPE | Database type

TODO document available db_types and conn strings

## Development

```
GITBI_REPO_DIR="./tests/gitbi-testing" ./start_app.sh

GITBI_REPO_DIR="./tests/gitbi-testing" pytest
```
