#!/usr/bin/python3 
import sys
import ipaddress
import re
import platform
import os
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import timeit

'''
1-Take any amount of arguments and verify each argument matches an IP
2-Ping each IP using mulithreading, obtain the response as "good" or "request timed out"
3-Displays which IPs are up and which IPs are not responding to pings
'''

IP = sys.argv[1:]
address_array = []

def ping_address(address):
    count_option = '-n' if platform.system().lower()=='windows' else '-c'
    ping_response = (os.system("ping " + count_option +  " 1 -W2 " + address + " > /dev/null 2>&1"))
    
    if ping_response == 0:
        print(f"Host is alive: {address}")
        
def main():
    if (IP):
        for address in IP:
            ip_match = re.search(r"^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?$", address) # Match IP or CIDR
            if ip_match:
                for ip in ipaddress.IPv4Network(address, False):
                    address_array.append(str(ip)) # Removes IPv4Address text
            else:
                print(f"Incorrect address: {address}")
        if (address_array):
            with ThreadPoolExecutor(max_workers=10) as executor:
                pool = multiprocessing.Pool(multiprocessing.cpu_count())
                results = pool.map(ping_address, address_array)
                pool.close()
    else:
        print('''No arguments passed
    Usage: ./MultipleIPPings.py X.X.X.X. X.X.X.X.
        ''')
        sys.exit()
if __name__ == "__main__":
    print("Time: {}".format(timeit.Timer(main).timeit(number=1)))