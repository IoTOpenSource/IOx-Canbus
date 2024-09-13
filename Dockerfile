# Use Alpine image as the base image for the build stage
FROM alpine:3.15 AS build-stage

# Install necessary packages and dependencies
RUN apk update && \
    apk add --no-cache python3 py3-pip build-base python3-dev vim && \
    pip3 install --upgrade pip

# Copy the requirements.txt file and install dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --ignore-installed -r requirements.txt

# Use Alpine image as the base image for the production stage
FROM alpine:3.15 AS prod-stage

# Install runtime dependencies
RUN apk update && \
    apk add --no-cache python3 py3-pip can-utils vim

# Copy installed Python packages from the build stage
COPY --from=build-stage /usr/lib/python3.9/site-packages /usr/lib/python3.9/site-packages
COPY --from=build-stage /usr/bin/python3 /usr/bin/python3

# Copy the application files
COPY . /app

# Ensure the startup script is in the correct location
COPY startup.sh /startup.sh

# Set the working directory
WORKDIR /app

# Make the startup script executable
RUN chmod +x /startup.sh

# Expose the port the app runs on
EXPOSE 9001

# Command to run the application
CMD ["/bin/sh", "-c", "/startup.sh"]
