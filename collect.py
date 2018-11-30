""" Collects user behavior data at a fixed interval. """

""" ---- Created by CMouse (qt2126@columbia.edu) ---- """

import argparse
import logging
import os
from time import asctime, localtime, sleep

import psutil
from watchdog.observers import Observer
from AppKit import NSWorkspace

from eventhandler import CustomFileSystemEventHandler

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def parse_args():
    """ Parse command line arguments. """
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

def main():
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
    
    workspace = NSWorkspace.sharedWorkspace()
    
    # Warm Start
    pc_set, pc_created, pc_deleted = collect_process(pc_set)
    nt_set, nt_opened, nt_closed = collect_network(nt_set)
    prev_app = workspace.activeApplication()["NSApplicationName"]
    sleep(1)

    handler.clear() # clear statistics
    app_switched = 0  # clear statistics
    
    # Collect
    try:
        while True:
            for _ in range(args.interval * 60):
                curr_app = workspace.activeApplication()["NSApplicationName"]
                if curr_app != prev_app:
                    logger.debug("App switch from {} to {}".format(prev_app, curr_app))
                    app_switched += 1
                prev_app = curr_app
                sleep(1)
            
            pc_set, pc_created, pc_deleted = collect_process(pc_set)
            nt_set, nt_opened, nt_closed = collect_network(nt_set)

            results = (pc_created, pc_deleted, nt_opened, nt_closed, handler.created, handler.deleted, handler.modified, handler.moved, app_switched)
            fout.write(str(results) + '\n')
            fout.flush()
            if args.verbose:
                verbose_print(results)
            
            handler.clear() # clear statistics
            app_switched = 0  # clear statistics
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
    fout.close()

def verbose_print(results):
    print("----------------------------------------")
    print(asctime(localtime()))
    print("Number of processes created: {}".format(results[0]))
    print("Number of processes deleted: {}".format(results[1]))
    print("Number of ports opened: {}".format(results[2]))
    print("Number of ports closed: {}".format(results[3]))
    print("Number of files created: {}".format(results[4]))
    print("Number of files deleted: {}".format(results[5]))
    print("Number of files modified: {}".format(results[6]))
    print("Number of files moved: {}".format(results[7]))
    print("Number of apps switched: {}".format(results[8]))
    print("----------------------------------------")

if __name__ == "__main__":
    main()
