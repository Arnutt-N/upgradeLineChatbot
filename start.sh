#!/bin/bash
# start.sh
exec gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --host 0.0.0.0 --port $PORT
