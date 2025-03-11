#! /bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/env.sh"

stop.sh

supervisord -c supervisord.conf

supervisorctl -c supervisord.conf status

echo "Supervisor setup and started successfully!"
