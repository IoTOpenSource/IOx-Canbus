# Car Diagnostics IOx Application

## Description
This IOx application serves as a base platform for users who want to remotely access and display car diagnostics through a Cisco router. Users can either deploy the pre-built application package directly or use the code from this repository to build their own Docker image and create a custom IOx application package.

## Prerequisites
- Cisco router that supports IOx
- Docker environment for building custom images (optional)
- Basic understanding of Docker and Cisco IOx applications

## Installation
You can install the Car Diagnostics IOx Application in two ways:

### Using the Pre-built Application Package
1. Download the pre-built package from the Releases section.
2. Follow the standard procedure to deploy an IOx application on your Cisco router (see Cisco's official documentation for details).
3.  Ensure port 9000 is open and assigned for this application's use on your router. This port is used for accessing the application interface remotely.

### Configuration and Network Setup
- Open the router's configuration interface.
- Navigate to the port settings.
- Assign port 9000 to the Car Diagnostics IOx Application to ensure proper functionality and remote accessibility.

### Building from Source
1. Clone this repository:
   ```bash
   https://github.com/IoTOpenSource/IOx-Canbus.git
2. Navigate to the cloned directory:
   ```bash
   cd IOx-Canbus
3. Build your docker.
4. Use the IOx client tools to package your Docker image into an IOx application package.
5. Deploy the packaged application to your Cisco router.
