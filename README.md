# seligson-taskusalkku-backend

Backend for taskusalkku, pointing to Api specs.

##Clone:
```bash
git clone --recurse-submodules git@github.com:Metatavu/seligson-taskusalkku-backend.git
```
For both local and docker setup first go to the repo directory
```bash
cd seligson-taskusalkku-backend
```

##Setup:

###1.Docker
Build development:
```bash
docker build -t seligson-taskusalkku-backend --target development src/
```
Build production:
```bash
docker build -t seligson-taskusalkku-backend --target production src/
```

Run
development
```bash
docker run --net=host -it --rm --name development seligson-taskusalkku-backend
```
production
```bash
docker run --net=host -it --rm --name production seligson-taskusalkku-backend
```

###2.Local
Install Python 3.9 on your local
```bash
sudo apt install python3.9 python3.9-dev python3.9-venv
```

Install the mysql client related packages.

```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
```

```bash
python3 -m venv  venv
source venv/bin/activate
set -o allexport && source env.sh && set +o allexport
cd src
pip install -r requirements-dev.txt  # for development purposes
```

Run:
```bash
cd src
uvicorn app.main:app --reload
```

### 3.Tests
Prepare environment as mentioned above
```bash
source venv/bin/activate
pytest
```

if it fails, you can run tests for the first time like this:
```bash
docker build -t seligson-sync -f src/Dockerfile-sync src/ &&  pytest --setup-show -s -o log_cli=true
```


##Ping:
```bash
http://127.0.0.1:8000/v1/system/ping
```

## Code generating from API Specification
Basically you don't need to do these configurations to run the current implementation, and it is for development purpose. 
- generating the spec
make sure you are in git root folder
```bash
sudo apt install maven
sudo apt-get install jq
./bin/utils/generate-spec.sh # make sure you are in git root folder
```
- generating the output for the api
make sure you are in git root folder
```bash
./bin/utils/openapi-generator-cli.sh author template -g python-fastapi
bin/utils/generate-spec.sh
```

