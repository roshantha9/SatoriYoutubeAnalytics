import sys
import threading

logger = None

class SubscriptionObserver(object):

    def __init__(self, log_handler, mailbox=None):
        global logger
        logger = log_handler

        if mailbox == None:
            self.mailbox = []
        else:
            self.mailbox = mailbox

        self.got_message_event = threading.Event()




    def on_subscription_data(self, data):
        #logger.debug("on_subscription_data:: Enter")
        #self.mailbox = []
        for message in data['messages']:
            self.mailbox.append(message)
        self.got_message_event.set()


    def on_enter_subscribing(self):
        logger.debug("on_enter_subscribing:: Enter")
    def on_enter_subscribed(self):
        logger.debug("on_enter_subscribed:: Enter")
    def on_enter_unsubscribing(self):
        logger.debug("on_enter_unsubscribing:: Enter")
    def on_enter_unsubscribed(self):
        logger.debug("on_enter_unsubscribed:: Enter")
    def on_enter_failed(self):
        logger.debug("on_enter_failed:: Enter")
    def on_deleted(self):
        logger.debug("on_deleted:: Enter")
    def on_created(self):
        logger.debug("on_created:: Enter")


    def clear_mailbox(self):
        self.mailbox = []
