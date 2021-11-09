#!/bin/bash

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR=$(realpath $SCRIPT_DIR/../../)
rm -fR $PROJECT_DIR/generated
mkdir -p generated
$SCRIPT_DIR/openapi-generator-cli.sh generate -i taskusalkku-spec/swagger.yaml -g python-fastapi -o $PROJECT_DIR/generated --config $PROJECT_DIR/generator-config.json -t openapi-templates
rm -fR src/spec
rm -f $PROJECT_DIR/generated/src/spec/main.py
rm -f $PROJECT_DIR/generated/src/spec/security_api.py
cp -R $PROJECT_DIR/generated/src/spec src/spec
rm -fR $PROJECT_DIR/generated