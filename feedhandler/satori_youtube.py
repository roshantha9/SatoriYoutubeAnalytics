import sys
import time
import pprint
import logging
import json
from colorlog import ColoredFormatter

from satori.rtm.client import make_client, SubscriptionMode


# local imports
from SatoriSubscriptionHandler import SubscriptionObserver


# constants
LOG_LEVEL = logging.DEBUG
DELAY = 1.0 # seconds
TIMEOUT = 30 # seconds


def setup_satori():
    """ Return a satori config (credentials and/or settings) """
    with open('credentials.json') as json_data_file:
        data = json.load(json_data_file)
        creds = {
            'endpoint' : data['satori-credentials']['endpoint'],
            'appkey' : data['satori-credentials']['appkey'],
            'channel' : data['satori-credentials']['channel']
        }
        return creds

def setup_logger():
    """Return a logger with a default ColoredFormatter."""
    formatter = ColoredFormatter(
        "%(log_color)s %(asctime)s %(levelname)-8s%(reset)s %(log_color)s%(message)s",
        datefmt="%y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red',
        }
    )
    logger = logging.getLogger('example')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)

    return logger


def debug_satori_messages(subscription_observer):
    for i, message in enumerate(subscription_observer.mailbox):
        print i, message['snippet']['title'].strip()

    subscription_observer.clear_mailbox()



def main():
    """ Main body - subscribes to a channel and receives messages """

    ## initialisation ##
    logger = setup_logger()
    satori_credentials= setup_satori()
    endpoint = satori_credentials['endpoint']
    appkey = satori_credentials['appkey']
    channel = satori_credentials['channel'] # youtube-videos

    # connect to satori data stream
    with make_client(endpoint=endpoint, appkey=appkey) as client:
        logger.info("Connected to Satori RTM")
        logger.info('Press CTRL-C to exit')

        # subscribe to a channel
        subscription_observer = SubscriptionObserver(logger)  # subscription service
        client.subscribe(channel, SubscriptionMode.SIMPLE, subscription_observer)



        try:
            while True:
                if not subscription_observer.got_message_event.wait(TIMEOUT):
                    logger.error("Channel subscription timeout !")
                    sys.exit()

                subscription_observer.got_message_event.clear() # clear mutex

                debug_satori_messages(subscription_observer)
                time.sleep(DELAY)

        # cntrl-c to exit
        except KeyboardInterrupt:
            client.unsubscribe(channel)
            sys.exit("KeyboardInterrupt received")
            pass






if __name__ == '__main__':
    main()
