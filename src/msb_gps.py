import logging
import zmq
import logging
import sys
import gps
import json

try:
    from config import init
except ImportError:
    logging.fatal('failed to import init method')
    sys.exit(-1)

def main():
    config = init()

    try:
        gpsd_socket = gps.gps(mode=gps.WATCH_ENABLE)
    except Exception as e:
        logging.fatal('failed to connect to gpsd')
        sys.exit(-1)

    connect_to = f'{config["ipc_protocol"]}:///tmp/msb:{config["ipc_port"]}'
    logging.debug(f'binding to {connect_to} for zeroMQ IPC')
    ctx = zmq.Context()
    zmq_socket = ctx.socket(zmq.PUB)

    try:
        zmq_socket.connect(connect_to)
    except Exception as e:
        logging.fatal('failed to connect to zeroMQ socket for IPC')
        sys.exit(-1)

    logging.debug(f'connected to zeroMQ IPC socket')

    logging.debug(f'entering endless loop')

    try:
        while True:
            # Do stuff
            report = gpsd_socket.next().__dict__
            if report['class'] == 'TPV':
                
                if config['print']: print(json.dumps(report))

                zmq_socket.send_pyobj(report)

    except StopIteration:
        logging.fatal("GPSD has terminated")

    except KeyboardInterrupt:
        logging.info('goodbye')


if __name__ == '__main__':
    main()
