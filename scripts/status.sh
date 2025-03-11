#!/bin/bash

if pgrep -x "supervisord" >/dev/null; then
    supervisorctl -c supervisord.conf status
else
    echo "Supervisor is not running."
    exit 1
fi
