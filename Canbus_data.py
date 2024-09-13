import can
import json
import time
import struct
import os
import logging
import serial
import pynmea2
from logging.handlers import RotatingFileHandler
from serial.serialutil import SerialException

# Environment variables
LOOP_INTERVAL = int(os.getenv('LOOP_INTERVAL'))
VEHICLE_SPEED_DIV = int(os.getenv('VEHICLE_SPEED_DIV'))
ENGINE_RPM_DIV = int(os.getenv('ENGINE_RPM_DIV'))
FUEL_LEVEL_DIV = int(os.getenv('FUEL_LEVEL_DIV'))
TRIP_TIME_DIV = int(os.getenv('TRIP_TIME_DIV'))
ODOMETER_DIV = int(os.getenv('ODOMETER_DIV'))
COOLANT_TEMP_DIV = int(os.getenv('COOLANT_TEMP_DIV'))
INTAKE_AIR_TEMP_DIV = int(os.getenv('INTAKE_AIR_TEMP_DIV'))
LOCATION_DIV = int(os.getenv('LOCATION_DIV'))
DEBUG_VERBOSE = int(os.getenv('DEBUG_VERBOSE'))
CAF_APP_LOG_DIR = os.getenv("CAF_APP_LOG_DIR", "/tmp")
CAN_CHANNEL = os.getenv('CAN_CHANNEL', 'vxcan0')
#IR_GPS = os.getenv('IR_GPS')

# Initialize logger
log_file_path = os.path.join(CAF_APP_LOG_DIR, "iox-vehicle-obd2.log")
logger = logging.getLogger(__name__)
if DEBUG_VERBOSE == 0:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

handler = RotatingFileHandler(log_file_path, maxBytes=5000000, backupCount=1)
log_format = logging.Formatter('[%(asctime)s]{%(pathname)s:%(lineno)d}%(levelname)s- %(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)

# Initialize CAN bus
canbus = can.Bus(channel=CAN_CHANNEL, interface='socketcan', bitrate=250000)

# Retry logic for initializing GPS serial connection
#gpsser = serial.Serial(IR_GPS ,115200, timeout=2)

def ReqPID(channel, PID):
    reqTimeout = 3
    msg = can.Message(arbitration_id=0x7DF, data=[2,1,PID,170,170,170,170,170], is_extended_id=False)
    channel.send(msg)
    sendTime = time.time()
    while (time.time() - sendTime) < reqTimeout:
        msg = channel.recv(timeout=reqTimeout)
        if msg and msg.arbitration_id == 2024 and msg.data[1] == 65 and msg.data[2] == PID:
            return msg
    return None

def getSupported(bus, PID):
    supportedPID = '0' * 32
    message = ReqPID(bus, PID)
    if message:
        tempArray = bytearray([message.data[3], message.data[4], message.data[5], message.data[6]])
        supportedPID = ''.join(bin(x)[2:].zfill(8) for x in tempArray)
    return supportedPID

def ReqLocation(ser):
    reqTimeout = 3
    tempPayload = {}
    ser.flushInput()
    startTime = time.time()
    while (time.time() - startTime) < reqTimeout:
        line = ser.readline().decode('utf-8')
        if line.startswith('$'):
            try:
                msg = pynmea2.parse(line)
                if msg.sentence_type == 'GGA':
                    lat = msg.latitude
                    lon = msg.longitude
                    num_sats = msg.num_sats
                    altitude = msg.altitude
                    altitude_units = msg.altitude_units
                    horizontal_dil = msg.horizontal_dil
                    gps_qual = msg.gps_qual
                    if gps_qual != 0:
                        tempPayload = {
                            'lat': lat,
                            'lon': lon,
                            'num_sats': num_sats,
                            'altitude': altitude,
                            'altitude_units': altitude_units,
                            'horizontal_dil': horizontal_dil,
                            'gps_qual': gps_qual
                        }
                    else:
                        tempPayload = {'gps_qual': gps_qual, 'num_sats': num_sats}
                    return tempPayload
            except:
                pass
    return None

def fetch_canbus_data():
    timestamp = int(time.time() * 1000)
    tempPayload = {}

    # Check for supported PIDs
    tempPayload['canbusActive'] = 0
    supported_PID_01_20 = getSupported(canbus, 0)
    if supported_PID_01_20 != ('0' * 32):
        tempPayload['canbusActive'] = 1
    supported_PID_21_40 = '0' * 32
    supported_PID_41_60 = '0' * 32
    supported_PID_61_80 = '0' * 32
    supported_PID_81_A0 = '0' * 32
    supported_PID_A1_C0 = '0' * 32

    if supported_PID_01_20[32-1] == '1':
        supported_PID_21_40 = getSupported(canbus, 32)
    if supported_PID_21_40[32-1] == '1':
        supported_PID_41_60 = getSupported(canbus, 64)
    if supported_PID_41_60[32-1] == '1':
        supported_PID_61_80 = getSupported(canbus, 96)
    if supported_PID_61_80[32-1] == '1':
        supported_PID_81_A0 = getSupported(canbus, 128)
    if supported_PID_81_A0[32-1] == '1':
        supported_PID_A1_C0 = getSupported(canbus, 160)

    logger.debug("Supported PIDs: 01-20: %s, 21-40: %s, 41-60: %s, 61-80: %s, 81-A0: %s, A1-C0: %s", supported_PID_01_20, supported_PID_21_40, supported_PID_41_60, supported_PID_61_80, supported_PID_81_A0, supported_PID_A1_C0)

    # Vehicle Speed
    if VEHICLE_SPEED_DIV != 0 and supported_PID_01_20[12] == '1':
        message = ReqPID(canbus, 13)
        if message:
            tempData = message.data[3]
            tempPayload['vehicleSpeed'] = {'value': tempData, 'unit': 'kmph'}
            logger.debug("Vehicle Speed: %s", tempData)

    # Engine RPM
    if ENGINE_RPM_DIV != 0 and supported_PID_01_20[11] == '1':
        message = ReqPID(canbus, 12)
        if message:
            tempArray = bytearray([message.data[3], message.data[4]])
            tempData = (struct.unpack('>H', tempArray)[0]) / 4
            tempPayload['engineRPM'] = {'value': tempData, 'unit': 'rpm'}
            logger.debug("Engine RPM: %s", tempData)

    # Fuel tank level
    if FUEL_LEVEL_DIV != 0 and supported_PID_21_40[14] == '1':
        message = ReqPID(canbus, 47)
        if message:
            tempData = round(((100 / 255) * message.data[3]), 2)
            tempPayload['fuelLevel'] = {'value': tempData, 'unit': 'percent'}
            logger.debug("Fuel Level: %s", tempData)

    # Time since engine start
    if TRIP_TIME_DIV != 0 and supported_PID_01_20[30] == '1':
        message = ReqPID(canbus, 31)
        if message:
            tempArray = bytearray([message.data[3], message.data[4]])
            tempData = struct.unpack('>H', tempArray)[0]
            tempPayload['tripTime'] = {'value': tempData, 'unit': 'seconds'}
            logger.debug("Time since engine start: %s", tempData)

    # Odometer
    if ODOMETER_DIV != 0 and supported_PID_A1_C0[5] == '1':
        message = ReqPID(canbus, 166)
        if message:
            tempArray = bytearray([message.data[3], message.data[4], message.data[5], message.data[6]])
            tempData = round(((struct.unpack('>I', tempArray)[0]) / 10), 2)
            tempPayload['odometer'] = {'value': tempData, 'unit': 'km'}
            logger.debug("Odometer: %s", tempData)

    # Engine coolant temperature
    if COOLANT_TEMP_DIV != 0 and supported_PID_01_20[4] == '1':
        message = ReqPID(canbus, 5)
        if message:
            tempData = message.data[3] - 40
            tempPayload['engineCoolantTemp'] = {'value': tempData, 'unit': 'C'}
            logger.debug("Engine Coolant Temp: %s", tempData)

    # Intake air temperature
    if INTAKE_AIR_TEMP_DIV != 0 and supported_PID_01_20[14] == '1':
        message = ReqPID(canbus, 15)
        if message:
            tempData = message.data[3] - 40
            tempPayload['intakeAirTemp'] = {'value': tempData, 'unit': 'C'}
            logger.debug("Intake Air Temp: %s", tempData)

    # Fetch GPS location data
    # if LOCATION_DIV != 0:
    #     location_data = ReqLocation(gpsser)
    #     if location_data:
    #         tempPayload['location'] = location_data

    tempPayload['timestamp'] = timestamp
    return tempPayload
