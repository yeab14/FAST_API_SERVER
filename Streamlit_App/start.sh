#!/bin/bash
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4 --timeout-keep-alive 120



