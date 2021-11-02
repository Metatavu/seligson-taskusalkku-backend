## seligson-taskusalkku-backend

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

Build test:
```bash
docker build -t seligson-taskusalkku-backend --target test src/
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
test
```bash
docker run --net=host -it --rm --name test seligson-taskusalkku-backend pytest
```


###2.Local
Install Python 3.6+ on your local(tested only with python 3.8)
```bash
python3 -m venv  venv
source venv/bin/activate
cd src
pip install -r requirements-dev.txt  # for development purposes
```
Run:
```bash
cd src
uvicorn app.main:app --reload
```

##Ping:
```bash
http://127.0.0.1:8000/v1/system/ping
```

## Code generating from API Specification
```bash
fastapi-codegen --input taskusalkku-spec/swagger.yaml --output app
```
