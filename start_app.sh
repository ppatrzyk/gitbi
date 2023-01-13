#!/bin/bash

set -e

app_dir="$(realpath ./app)";
if [ -n "$GITBI_REPO_DIR" ]; then
    echo "GITBI_REPO_DIR specified: $GITBI_REPO_DIR"
else
    echo "GITBI_REPO_DIR not specified, running example configuration"
    git clone https://github.com/ppatrzyk/gitbi-example.git
    GITBI_REPO_DIR=./gitbi-example
    git -C $GITBI_REPO_DIR checkout example
    export GITBI_POKEMON_TYPE=sqlite
    export GITBI_POKEMON_CONN="$(realpath ./gitbi-example/pokemon.sqlite)"
fi
export GITBI_REPO_DIR="$(realpath $GITBI_REPO_DIR)";
cd $GITBI_REPO_DIR;

inside_git_repo="$(git rev-parse --is-inside-work-tree)";
toplevel="$(git rev-parse --show-toplevel)";
if [ $GITBI_REPO_DIR != $toplevel ]; then
    echo "Passed subdirectory of an existing git repo at $toplevel";
    exit 1
else
    past_commits=$(git log);
fi;

echo "Git repo OK, starting gitbi...";
cd $app_dir
uvicorn \
    --host=0.0.0.0 \
    --port=8000 \
    --log-level=debug \
    --workers=1  \
    --app-dir=$app_dir \
    main:app
