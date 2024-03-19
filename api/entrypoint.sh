#!/bin/bash

# Start Xvfb on display 99 with screen 0
Xvfb :99 -screen 0 1280x720x16 &

# Execute the Docker CMD
exec "$@"