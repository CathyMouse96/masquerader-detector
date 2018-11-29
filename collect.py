""" Collects user behavior data at a fixed interval. """

# Created by CMouse (qt2126@columbia.edu)

import argparse
import logging
import os
from time import asctime, localtime, sleep

import psutil
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interval', default=5, type=int, 
        help='The interval (minutes) between two consecutive collections.')
    parser.add_argument('-m', '--monitor_dir', default=os.path.expanduser('~/Documents'), type=str,
        help='The directory to monitor for file system events.')
    parser.add_argument('-o', '--output_dir', default='data', type=str,
        help='The path to output directory.')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Run in verbose mode.')
    return parser.parse_args()

def collect_process(prev_set):
    """ Collects the number of processes created and deleted. """
    curr_set = set() # store the current processes
    for process in psutil.process_iter(attrs=['exe', 'pid']):
        exe = process.exe # process executable
        pid = process.pid # process id
        curr_set.add((exe, pid))
    
    created = len(curr_set - prev_set) # number of processes created
    deleted = len(prev_set - curr_set) # number of processes deleted
    return curr_set, created, deleted
    
def collect_network(prev_set):
    """ Collects the number of ports opened and closed. """
    curr_set = set() # store the current connections
    for connection in psutil.net_connections():
        fd = connection.fd # file descriptor
        laddr = connection.laddr # local address
        raddr = connection.raddr # remote address
        if not raddr or raddr.ip == laddr.ip: # filter local connections
            continue
        curr_set.add((fd, laddr.ip, laddr.port, raddr.ip, raddr.port))
    
    opened = len(curr_set - prev_set) # number of ports opened
    closed = len(prev_set - curr_set) # number of ports closed
    return curr_set, opened, closed

class CustomFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.created = 0
        self.deleted = 0
        self.modified = 0
        self.moved = 0
    
    def on_created(self, event):
        logger.debug("Created: " + event.src_path)
        self.created += 1
    
    def on_deleted(self, event):
        logger.debug("Deleted: " + event.src_path)
        self.deleted += 1
    
    def on_modified(self, event): # Excluded from features
        logger.debug("Modified: " + event.src_path)
        self.modified += 1
    
    def on_moved(self, event):
        logger.debug("Moved: " + event.src_path)
        self.moved += 1
    
    def clear(self):
        self.__init__()

args = parse_args()

# Create output file
filename = "-".join(str(x) for x in localtime()) + ".log"
fout = open(os.path.join(args.output_dir, filename), 'a')

# Initialize
pc_set = set() # set of processes
nt_set = set() # set of network connections

handler = CustomFileSystemEventHandler()
observer = Observer()
observer.schedule(handler, args.monitor_dir, recursive=True)
observer.start()

# Warm Start
pc_set, pc_created, pc_deleted = collect_process(pc_set)
nt_set, nt_opened, nt_closed = collect_network(nt_set)
handler.clear() # clear statistics
sleep(args.interval * 60)

# Collect
try:
    while True:
        pc_set, pc_created, pc_deleted = collect_process(pc_set)
        nt_set, nt_opened, nt_closed = collect_network(nt_set)
        if args.verbose:
            print("----------------------------------------")
            print(asctime(localtime()))
            print("Number of processes created: {}".format(pc_created))
            print("Number of processes deleted: {}".format(pc_deleted))
            print("Number of ports opened: {}".format(nt_opened))
            print("Number of ports closed: {}".format(nt_closed))
            print("Number of files created: {}".format(handler.created))
            print("Number of files deleted: {}".format(handler.deleted))
            print("Number of files modified: {}".format(handler.modified))
            print("Number of files moved: {}".format(handler.moved))
            print("----------------------------------------")
        handler.clear() # clear statistics
        sleep(args.interval * 60)
except KeyboardInterrupt:
    observer.stop()

observer.join()
fout.close()
