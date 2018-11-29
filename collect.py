""" Collects user behavior data at a fixed interval. """

# Created by CMouse (qt2126@columbia.edu)

import argparse
import os
from time import localtime, sleep

import psutil
import watchdog

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interval', default=5, type=int, 
        help='The interval (minutes) between two consecutive collections.')
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

args = parse_args()

# Create output file
filename = "-".join(str(x) for x in localtime())
fout = open(os.path.join(args.output_dir, filename), 'a')

# Initialize
pc_set = set() # set of processes
nt_set = set() # set of network connections

# Warm Start
pc_set, pc_created, pc_deleted = collect_process(pc_set)
nt_set, nt_opened, nt_closed = collect_network(nt_set)
sleep(args.interval * 60)

# Collect
try:
    while True:
        pc_set, pc_created, pc_deleted = collect_process(pc_set)
        nt_set, nt_opened, nt_closed = collect_network(nt_set)
        # fout.write("hi!")
        if args.verbose:
            print("----------------------------------------")
            print(localtime())
            print("Number of processes created: {}".format(pc_created))
            print("Number of processes deleted: {}".format(pc_deleted))
            print("Number of ports opened: {}".format(nt_opened))
            print("Number of ports closed: {}".format(nt_closed))
            print("----------------------------------------")
        sleep(args.interval * 60)
except KeyboardInterrupt:
    pass

fout.close()
