#!/bin/bash

set -e

app_dir="$(realpath ./app)";
export gitbi_repo_dir="$(realpath $1)";
cd $gitbi_repo_dir;

inside_git_repo="$(git rev-parse --is-inside-work-tree)";
toplevel="$(git rev-parse --show-toplevel)";
if [ $gitbi_repo_dir != $toplevel ]; then
    echo "Passed subdirectory of an existing git repo at $toplevel";
    exit 1
else
    past_commits=$(git log);
fi;

echo "Git repo OK, starting gitbi...";
uvicorn \
    --host=127.0.0.1 \
    --port=8000 \
    --log-level=debug \
    --workers=1  \
    --app-dir=$app_dir \
    main:app
