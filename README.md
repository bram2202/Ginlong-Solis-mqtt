# Ginlong Solis mqtt/pv-output
Getting Ginlong Solis invertor data and posting on MQTT / PV output.

Using a docker image as a service to read the invertor via the RS485 port.

The measurements are send to mqtt every 5 seconds, and to PV output every 5 minutes.

# Requirements
- RS485 to USB converter.

# Connections
Connecting the converter straight to the invertor.

The pins are a little bigger that standard breadboard, you need something that would fit.

I used the wires of the female side of a PCI-E power connector and compressed it a little.

The connector pins on the Solis invertor are tagged with a number, just take a close look. 

| Solis invertor | RS485 to USB |
|:---- |:----|
|1|nc|
|2|nc|
|3|A+|
|4|B-|

# Docker compose

```yaml
version: "2.1"
services:
  doods:
    image: test-pv
    container_name: ginlong-Solis-pvoutput
    environment:
      - USB_SERIAL=/dev/ttyUSB0
      - BROKER_IP=<IP of mqtt broker>
      - BROKER_PORT=1883
      - BROKER_USER=<mqtt user>
      - BROKER_PASSWORD=<mqtt password>
      - PV_OUTPUT_SYSTEM_ID=<PVOutput system ID>
      - PV_OUTPUT_API_KEY=<PVOutput api key>
    restart: unless-stopped
```

# Env vars

| vars | default | Description |
|:---- |:----|:----|
| mqtt_broker | - |  IP of mqtt broker |
| mqtt_port | 1883 | Port of mqtt broker |
| mqtt_user | - | user name for mqtt |
| mqtt_password | - | password for mqtt |
| pv_api_key | - | Your PVOutput api key |
| pv_system_id | -  | Your PVOutput system ID |

# MQTT topics

| Topic | Description |
|:---- |:----|
| pv/ac | All AC related values |
| pv/dc | All DC related values  |
| pv/gen | ALL generation values  |
| pv/temp | Temperature value |

## Values

Every topic contains a json with values

### AC
| Value | Description | unit |
|:---- |:----|:----|
| W | Watts | W |
| V | Volts | V |
| C | Current | A |
| F | Frequency |  Hz |

### DC
| Value | Description | unit |
|:---- |:----|:----|
| V | Volt | V |
| C | Current | A |

### GEN
| Value | Description | unit |
|:---- |:----|:----|
| D | Generated today | kWh |
| T | Generated all time | kWh |

### temp
| Value | Description | unit |
|:---- |:----|:----|
| T | Inverter temperature |  C |
