#!/bin/bash

echo "==================================="
echo "Starting File Converter Application"
echo "==================================="
echo ""

# Check if Redis is running
echo "Checking if Redis is running..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "[ERROR] Redis is not running!"
    echo "Please start Redis first:"
    echo "  redis-server"
    echo ""
    exit 1
fi
echo "[OK] Redis is running"

echo ""
echo "Starting Celery worker in background..."
celery -A fileconverter worker --loglevel=info &
CELERY_PID=$!

echo "Celery worker started with PID: $CELERY_PID"

sleep 3

echo ""
echo "Starting Django development server..."
echo ""
echo "Application will be available at:"
echo "  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Trap Ctrl+C to stop celery when server stops
trap "kill $CELERY_PID; exit" INT TERM

daphne -b 127.0.0.1 -p 8000 fileconverter.asgi:application

