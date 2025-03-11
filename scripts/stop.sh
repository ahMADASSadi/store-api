#! /bin/bash

supervisorctl -c supervisord.conf stop all

supervisorctl -c supervisord.conf shutdown

echo "Supervisor stopped successfully!"

PIDS=$(sudo lsof -t -i :8000)
if [[ -n "$PIDS" ]]; then
    echo "Stopping processes on port 8000..."
    sudo kill -9 $PIDS
    echo "Process on port 8000 stopped."
else
    echo "No web service on port 8000 is running."
fi
