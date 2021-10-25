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
Build:
```bash
docker build  -t seligson-taskusalkku-backend .
```
Run:
```bash
docker run  --net=host seligson-taskusalkku-backend 
```
Should be able to ping.

###2.Local
Install Python 3.6+ on your local(tested only with python 3.8)
```bash
python3 -m venv  venv
source venv/bin/activate
pip install -r requirements-dev.txt  # for development purposes
```
Run:
```bash
uvicorn app.main:app --reload
```

##Ping:
```bash
http://127.0.0.1/v1/system/ping
```

## Code generating from API Specification
```bash
fastapi-codegen --input taskusalkku-spec/swagger.yaml --output app
```