#!/usr/bin/env python
import asyncio
import json
import logging
import time
import sys
import os
import sqlite3


from aiodabpumps import DabPumpsApi

# Setup logging to StdOut
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

TEST_USERNAME = os.getenv('DAB_USER')
TEST_PASSWORD = os.getenv('DAB_PASS')
device_serial = os.getenv('DAB_SERIAL')

wanted_statuses = ["VP_PressureBar",                #2.9 bar ('29')
                   "PO_OutputPower",                #0.0 kW ('0')
                   "VF_FlowLiter",                  #0.0 l/min ('0') 
                   "TE_HeatsinkTemperatureC",       #22.0 °C ('220')
                   "StartNumber",                   #118
                   "Actual_Period_Flow_Counter",    #0.771 mc ('771')
                   "Actual_Period_Energy_Counter",  #0.5 kWh ('5')
                   "TotalEnergy"]                   # 0.7 kWh ('7')


async def main():
    api = None

    conn = sqlite3.connect('pump.db')
    cursor = conn.cursor()

    try:
        # Process these calls in the right order
        api = DabPumpsApi(TEST_USERNAME, TEST_PASSWORD)
        await api.async_login()

        while True:
            returned_statuses = []
            returned_statuses.append(int(time.time()))

            await api.async_fetch_device_statusses(device_serial)

            device_statusses = { k:v for k,v in api.status_map.items() if v.serial==device_serial }
            logger.debug(f"statusses: {len(device_statusses)}")

            for k,v in device_statusses.items():
                value_with_unit = f"{v.value} {v.unit}" if v.unit is not None else v.value

                for data_point in wanted_statuses:
                    if (v.key == data_point):
                        logger.info(f"{v.key}: {v.code}")
                        returned_statuses.append(int(v.code))

            logger.info(f"returned statuses: {returned_statuses}")
            try:
                 cursor.execute('INSERT INTO pump_status (date_time,  current_pressure,  motor_power, \
                                current_flow,  motor_temp, motor_start, flow_counter, energy_counter, \
                                total_energy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', returned_statuses)
            except sqlite3.IntegrityError as e:
                  logger.error(f"Error inserting data: {e}")

            # Commit the changes and close the connection
            rows_affected = cursor.rowcount
            if rows_affected > 0:
                print("Record inserted successfully!")
            else:
                print("Record not inserted.")
            conn.commit()
            
            time.sleep(10)

    except Exception as e:
        logger.error(f"Unexpected exception: {e}")

    finally:
        if api:
            await api.async_close()


asyncio.run(main())  # main loop
