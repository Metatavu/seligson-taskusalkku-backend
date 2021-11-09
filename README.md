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
Install Python 3.6+ on your local(tested only with python 3.8)
```bash
python3 -m venv  venv
source venv/bin/activate
```
copy environment variables and assign them
```bash
cp env_copy.sh env.sh
```
export them
```bash
export env.sh
```
install requirements
```bash
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

##Ping:
```bash
http://127.0.0.1:8000/v1/system/ping
```

## Code generating from API Specification
Basically you don't need to do this to run the current implementation, and it is for development purpose. 
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

## Schema creation
Basically this should only be done in the bootstrapping phase to represent external changes that are done to db.
You need to have the following dependencies installed in os.
```bash
#requirements for alchemy and autogeneration of code
sudo apt-get install mysql-server mysql-client libmysqlclient-dev
```
Run the generator
```bash
sqlacodegen --outfile db/models.py <SQLALCHEMY_DATABASE_URL>
```
