#!/bin/sh

# ============================================================
# This script is intended for internal use only.
# It sets up environment variables, starts necessary applications,
# and opens a specified port for a limited time.
# Use this script in a controlled environment with proper authorization.
# ============================================================

echo "Starting script for internal use only. Please ensure proper authorization to run this script."

# Export environment variables from the CAF_APP_CONFIG_FILE
for line in `grep -v '\[mainconfig\]' ${CAF_APP_CONFIG_FILE} | sed -e 's/ = /=/' | grep -v '^$'`;
do
    key=$(echo "$line" | cut -d'=' -f1)
    if ! env | grep -q "^$key="; then
        export $line
    fi
done

# Start the vehicle-obd2.py script
echo "Starting vehicle-obd2.py..."
python3 /app/app.py &

# Function to keep a connection port open for 60 seconds
keep_port_open_for_60_sec() {
    local PORT=$1
    echo "Opening port ${PORT} for 60 seconds for internal testing purposes..."

    # Use 'timeout' to limit the duration of the netcat listener
    timeout 60 nc -l -p $PORT -k >/dev/null 2>&1 & 

    # Wait for the timeout to finish and print a message
    wait $!
    echo "Port ${PORT} has been closed after 60 seconds."
}

# Run the port listener for 60 seconds in the background
keep_port_open_for_60_sec 12345   # Change '12345' to the desired port number

# Keep the container running
echo "Script setup complete. Container will keep running."
while true
do
    sleep 1
done
