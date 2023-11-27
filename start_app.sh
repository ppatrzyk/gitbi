#!/bin/bash

set -e

app_dir="$(realpath ./app)";
if [ -n "$GITBI_REPO_DIR" ]; then
    echo "GITBI_REPO_DIR specified: $GITBI_REPO_DIR"
else
    echo "GITBI_REPO_DIR not specified, running example configuration"
    if [ -d "./gitbi-example" ]; then
        echo "Example repo already exists, skipping clone"
    else
        git clone https://github.com/ppatrzyk/gitbi-example.git
    fi
    . ./gitbi-example/example_setup.sh
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
    --lifespan=on \
    --workers=1  \
    --app-dir=$app_dir \
    main:app
