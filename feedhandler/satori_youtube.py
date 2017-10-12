import sys
import time
from pprint import pprint
import logging
import json
import argparse
from colorlog import ColoredFormatter


# external frameworks APIs
from satori.rtm.client import make_client, SubscriptionMode

# local imports
from SatoriSubscriptionHandler import SubscriptionObserver
from elasticsearch import Elasticsearch
from ESHandler import ESHandler


# constants
LOG_LEVEL = logging.DEBUG
DELAY = 1.0 # seconds
TIMEOUT = 30 # seconds


#####################################################
# initialisation functions
#####################################################
def setup_satori(cred_fname):
    """ Return a satori config (credentials and/or settings) """
    assert (cred_fname != None), "Error! Credentials File not provided"

    with open(cred_fname) as json_data_file:
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




#####################################################
# Debug functions
#####################################################
def debug_satori_messages(subscription_observer, field='title'):
    if field == None:
        for i, message in enumerate(subscription_observer.mailbox):
            print "msg-"+ str(i) + ", " + str(message)
    else:
        for i, message in enumerate(subscription_observer.mailbox):
            print "msg-"+ str(i) + ", " + message['snippet'][field].strip()
            #print "msg-"+ str(i) + ", " + message['statistics']['view_count'].strip()
    print "---"

    #subscription_observer.clear_mailbox()


#####################################################
# Push messages to elastic
#####################################################
def store_satori_messages(subscription_observer, es):
    for i, message in enumerate(subscription_observer.mailbox):
        pushed_data = es.push_to_es(message)
        print "-- [", i, "] --"
        pprint(pushed_data)







#####################################################
# M A I N
#####################################################
def main(cred_fname=None, es_mapping_fname=None):
    """ Main body - subscribes to a channel and receives messages """

    ## initialisation ##
    logger = setup_logger()
    satori_credentials= setup_satori(cred_fname)
    endpoint = satori_credentials['endpoint']
    appkey = satori_credentials['appkey']
    channel = satori_credentials['channel'] # youtube-videos

    es = ESHandler(logger, es_mapping_fname)

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

                #debug_satori_messages(subscription_observer, field=None)

                store_satori_messages(subscription_observer, es)

                # clear all collected messages from satori
                subscription_observer.clear_mailbox()

                # wait before proceeding
                time.sleep(DELAY)

        # cntrl-c to exit
        except KeyboardInterrupt:
            client.unsubscribe(channel)
            sys.exit("KeyboardInterrupt received")
            pass




#####################################################
# Parse arguments
#####################################################
def argument_handler():
    # collect command line params
    parser = argparse.ArgumentParser(__file__, description="Collect Satori OpenData")
    parser.add_argument("--credentials", "-c", help="Credentials filename", default=None)
    parser.add_argument("--es_mapping", "-m", help="ES Index Mapping filename", default=None)


    args = parser.parse_args()

    return args



if __name__ == '__main__':

    args = argument_handler()

    main(cred_fname=args.credentials, es_mapping_fname=args.es_mapping)
