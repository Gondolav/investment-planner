source ./env/bin/activate
uvicorn --port 8000 --host 127.0.0.1 src.main:app --reload