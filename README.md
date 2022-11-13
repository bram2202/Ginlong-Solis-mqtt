# Ginlong Solis mqtt/pv-output
Getting Ginlong Solis invertor data and posting on MQTT / PV output.

Using a python script on linux as a service to read the invertor via the RS485 port.

The measurements are send to mqtt every 5 seconds, and to PV output every 5 minutes.

# Requirements
- RS485 to USB converter.
- Linux - Can be on a Respberry pi on or a full server.
- Python 3
- PIP

## Libraries
Use `pip install`
- paho-mqtt
- minimalmodbus
- schedule

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

# Vars

| vars | default | Description |
|:---- |:----|:----|
| mqtt_broker | - |  IP of mqtt broker |
| mqtt_port | 1883 | Port of mqtt broker |
| mqtt_user | - | user name for mqtt |
| mqtt_password | - | password for mqtt |
| pv_api_key | - | Your PVOutput api key |
| pv_system_id | -  | Your PVOutput system ID |


# Testing

After downloading the script and changing the values you can start it commandline the test it.
`printValues()` is commented out, enable it.

then run: `/usr/bin/python3 <script_location>/pv-inverter.py`

The values should be displayed.

The invertor needs to be running for this.


# Service
For running the script, i used a service to keep it running and starting at boot

## Create new 
`vim /lib/systemd/system/pv-script.service`

And add: (change path of script folder)

```
[Unit]
Description=PV output script
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
ExecStart=/usr/bin/python3  <YOUR-FOLDER>/pv-inverter.py
StandardInput=tty-force
Restart=always

[Install]
WantedBy=multi-user.target
```

## Start script

Reload the daemon:

`systemctl daemon-reload`

Start the script

`systemctl start pv-script.service`

Check the status

`systemctl status pv-script.service`

Start service at boot

`systemctl enable pv-script.service`


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
