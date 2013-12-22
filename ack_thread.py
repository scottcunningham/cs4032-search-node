import threading
from constants import *

class AckThread(threading.Thread):
    def __init__(self, node_id, event):
        self.node_id = node_id
        self.event = event

    def run():
        # Wait for an ACK for TIMEOUT_MS
        stop_event.wait(TIMEOUT_MS)
        # If we have waited until now and have not been stopped by
        # the calling program, then we have NOT received an ACK
        # from this node_id yet
        print "ERROR: No ACK received in max timeout (", TIMEOUT_MS, "ms)"
