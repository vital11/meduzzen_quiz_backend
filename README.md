## Quiz Project

#### Download
###### 
    $ mkdir code
    $ cd code
    $ git clone https://github.com/vital11/meduzzen_quiz_backend.git
    $ (env) pip install -r requirements.txt


#### Run
    $ (env) uvicorn app:main:app --reload
    Check it: http://127.0.0.1:8000 (Press CTRL+C to quit)
###### or
    $ (env)  docker-compose up --build
    Check it: http://127.0.0.1:8001 (Press CTRL+C to quit)


