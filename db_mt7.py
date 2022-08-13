# usb settings:
ID_VENDOR = 0x0eb8
ID_PRODUCT = 0xea02
import argparse
from datetime import datetime
from time import sleep

import pytz
import usb
from lxml import objectify, etree

tz = pytz.timezone('Europe/Amsterdam')

logger = None # Change to some python logger you like

# Setup
def connect():
    try:
        dev = usb.core.find(idVendor=ID_VENDOR, idProduct=ID_PRODUCT)
    except Exception as e:
        logger.error(f'No device found with id {ID_VENDOR} and {ID_PRODUCT}. Error {e}')
        return False

    if not dev:
        logger.error(f'No device found with id {ID_VENDOR} and {ID_PRODUCT}')
        return False
    logger.warning('Device connected!')
    return dev


MEAS_TYPE = {
    'MeasType1': 'ph',
    'MeasType2': 'orp',
    'MeasType3': 'conductivity',
    'TIMESTAMPS': 'status'
}

RESULT_NAME = {
    'ph': 'ResultPh',
    'orp': 'ResultPh',
    'conductivity': 'ResultCnd'
}


def run(measurement_id):
    data_saved = False

    logger.critical(f'Starting MT7 with measurement ID {measurement_id} to table mt7')

    dev = connect()
    # busy waiting for USB device to send data
    while True:
        data = {}
        time = datetime.now(tz=tz)
        if not dev:
            dev = connect()
            if not dev:
                logger.error('Reconnect dev failed.')
                data_saved = False
                sleep(1)
                continue
        try:
            ret = dev.read(0x81, 10, 2000)
        except usb.core.USBTimeoutError as e:
            logger.error(f'USB timeout: {e}')
            data_saved = False
            sleep(0.1)
            continue
        except usb.core.USBError as e:
            logger.error(f'Cannot read USB: {e}')
            dev = None
            data_saved = False
            sleep(1)
            continue
        except Exception as e:
            logger.error(f'Cannot read USB, other error: {e}')
            data_saved = False
            sleep(1)
            continue

        sret = ''.join([chr(x) for x in ret])
        sret = sret.strip()

        if '<EndOfMethod>' in sret:
            logger.error('Function closed. Waiting...')
            data_saved = False
            sleep(2)
            continue
        try:
            obj = objectify.fromstring(sret.encode())
        except etree.XMLSyntaxError as e:
            logger.error(f'Invalid read: {sret} \n error: {e}')
            data_saved = False
            continue
        if obj.ResultMessage.groupid == 'TIMESTAMPS':
            logger.error(f'Function closed or stability criteria reached. Waiting...')
            data_saved = False
            sleep(2)
            continue
        meas_type_raw = str(obj.ResultMessage.groupid).split(':')[0]
        try:
            meas_type = MEAS_TYPE[meas_type_raw]
            result_name = RESULT_NAME[meas_type]
        except KeyError:
            logger.warning(f'Invalid measure type {str(obj.ResultMessage.groupid)}\nMessage:{sret}')
            data_saved = False
            break
        except AttributeError:
            logger.warning(f'Invalid meas_type: {meas_type_raw}, invalid message received: {sret}')
            data_saved = False
            break

        try:
            data_db = {
                'time': time,
                'measurement_id': measurement_id,
                'mts_time': tz.localize(
                    datetime.strptime(str(obj.ResultMessage.result[result_name].timeStamp), '%Y-%m-%d %H:%M:%S')),
                'meas_type': meas_type,
                'temperature': float(obj.ResultMessage.result[result_name].rawTemperature),
                'raw_value': float(obj.ResultMessage.result[result_name].rawValue),
                'result_value': float(obj.ResultMessage.result[result_name].resultValue),
            }
        except Exception as e:
            logger.error(f'Cannot read Mettler-Toledo telegram. Skipping because {e}')
            data_saved = False
            continue

        logger.debug(data_db)  # [['measurement_id', 'time', 'mts_time']])
        if not data_saved:  # only log first time data saved
            logger.warning('Data save started!')
            data_saved = True
        # ins = TABLE_MT7.insert(values=data_db)
        # res = dbConnection.execute(ins)
        print(data_db)
        assert res, 'Fail db insert'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="MT7 values reader to database")
    parser.add_argument('--id', nargs='?', type=int, default=0, help='Measurement id')

    measurement_id = parser.parse_args().id
    if measurement_id == 0:  # default
        measurement_id = get_max_measurement_id() + 1

    run(measurement_id)
