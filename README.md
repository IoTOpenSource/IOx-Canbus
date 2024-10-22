# Car Diagnostics IOx Application Installation Guide

This guide walks you through the process of installing the Car Diagnostics IOx application on your Cisco router. The process includes downloading and deploying the application, configuring network ports, and ensuring policy compliance for web access.

---

## Prerequisites

Before you begin, make sure that you have:

1. A Cisco router that supports IOx applications.
2. Access to the router’s configuration interface (CLI or Web).
3. The Car Diagnostics IOx Application package (pre-built).
4. A basic understanding of Cisco networking commands.

---

## Installation Process

### Step 1: Download the Application Package

1. Visit the [Releases section](https://github.com/IoTOpenSource/IOx-Canbus/releases/tag/Appliacation) of this repository and download the latest **Car Diagnostics IOx Application** package.
   
2. Follow the standard procedure to deploy an IOx application on your Cisco router:
   - Refer to Cisco’s [official documentation](https://developer.cisco.com/docs/iox/#!iox/overview) for a detailed process on how to upload and install the application using the IOx Local Manager.

---

### Step 2: Port Configuration and Network Setup

To ensure the application functions correctly and can be accessed remotely, you need to assign specific ports and configure network settings.

1. **Open the Router’s Configuration Interface**
   - Login to the Cisco router using the CLI or Web UI.

2. **Assign Port for Application Access**
   - The Car Diagnostics IOx Application uses port `9001` for accessing its web-based interface.

3. **Assign the Port in the Router’s Configuration**
   Open the CLI and use the following command examples to configure port `9001` and other necessary ports:
   ```bash
      ip nat inside source static tcp 192.168.1.22 9001 interface GigabitEthernet0/0/0 9001
      ip access-list extended APP-PORT-9001
      10 permit tcp any host 192.168.1.22 eq 9001
   

**Example for additional port configurations**:
- **Port 9001** for NMEA communication:
  ```bash
  conf termso
  ip nat inside source static tcp <internal_ip_address> 9001 interface <interface_name> 9001
  ip access-list extended APP-PORT-9001
  10 permit tcp any host <internal_ip_address> eq 9001

Replace `<internal_ip_address>` and `<interface_name>` with the appropriate values for your network setup.

---

### Step 3: Web Access and Policy Implementation

If you are configuring any network security policies for accessing the Car Diagnostics IOx Application as a web app, ensure the following rules are implemented:

1. **Access Group Matching**
- Match the ports that the application is using with access groups to ensure proper security control. Example:
  ```bash
     match access-group name APP-PORT-9001


2. **Firewall Rules**
- Ensure that firewall rules allow inbound traffic to the router on the specified port (9001) based on the application’s services.

---

### Step 4: Test the Application

Once the application is installed and network configurations are applied, you can test its functionality:

1. Open a web browser and navigate to the router’s IP address with the assigned port `9001` to access the Car Diagnostics application interface.

Example:
http://<router_ip>:9001
or 
https://<router_ip>:9001


2. Make sure the application interface loads correctly and all diagnostic services are available.

---

### Additional Considerations

- Ensure that you follow best practices for security and network management when deploying this application in a production environment.
- If any issues arise during installation, refer to the Cisco IOx troubleshooting guide or raise an issue in this repository’s Issue section for community support.

---

## Example Network Policy for NMEA Traffic (Dead-Reckoning)

To handle UDP-based NMEA (National Marine Electronics Association) traffic for dead-reckoning scenarios, you can configure your network as follows:
```bash
   dead-reckoning nmea udp <source_ip_address> <destination_ip_address> 9001
```
This setup forwards UDP traffic from `<source_ip_address>` to the application on `<destination_ip_address>` at port `9001`.

---

## Conclusion

By following the above steps, you should be able to successfully install and configure the Car Diagnostics IOx application on your Cisco router. Make sure to assign the correct ports, configure network settings properly, and apply appropriate security policies to ensure smooth operation.

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
