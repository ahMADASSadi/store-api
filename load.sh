#!/bin/bash

# Check if the "scripts" directory exists in the current directory
if [ -d "./scripts" ]; then
  # Get the absolute path of the "scripts" directory
  SCRIPTS_DIR="$(pwd)/scripts"

  # Check if the "scripts" directory is already in the PATH
  if [[ ":$PATH:" != *":$SCRIPTS_DIR:"* ]]; then
    # Add the "scripts" directory to the PATH
    export PATH="$PATH:$SCRIPTS_DIR"
    echo "Added $SCRIPTS_DIR to PATH."
  else
    echo "$SCRIPTS_DIR is already in PATH."
  fi
else
  echo "No 'scripts' directory found in the current directory."
fi