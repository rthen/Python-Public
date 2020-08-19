#!/usr/local/bin/python3
# MAC address lookup using Wireshark's public Gitlab list
import requests
import re
import argparse
import sys
import os

def mac_lookup(mac):
    ws_mac_list= requests.get("https://gitlab.com/wireshark/wireshark/raw/master/manuf", allow_redirects=False)

    if ws_mac_list.status_code == 200:
        mac_search = re.search(r"{}.*".format(mac), ws_mac_list.text, re.IGNORECASE)
        try:
            mac_result = (mac_search.group())
            print(mac_result)
        except AttributeError:
            print(f"MAC address {mac} not found")
    else:
        print(f"Error opening Wireshark list. Status code: {ws_mac_list.status_code}")

def main():
    argparser = argparse.ArgumentParser(description="MAC address lookup using Wireshark's public Gitlab list.", usage="%(prog)s [options]")   
    argparser.add_argument("-p", "--path", action="store", metavar="", help="Path to file containing a list of MACs (supported tested files are csv, txt, xlsx, log)")
    argparser.add_argument("-i", "--input", nargs="+", metavar="", help="Enter one or more MAC address(es) direclty into the terminal")
    mac_regex = re.compile(r'([0-9a-fA-F]{2}[:-]){2}[0-9a-fA-F]{2}')

    # If no arguments are passsed, print the help page and exit
    if len(sys.argv) <= 1: 
        argparser.print_help() 
        sys.exit(0)
    args = argparser.parse_args()
    
    # Check which argument option is being passed
    if args.input:
        for mac in args.input:
            mac = mac.replace("-", ":") # Just easier to assume dashes needs to be replaced with colons
            try:
                matching_mac = re.search(mac_regex, mac)
                mac_lookup(matching_mac.group())
            except AttributeError as err:
                print(f"MAC address {mac} not in the correct format")
    else:
        mac_datafeed = args.path
        if os.path.isfile(mac_datafeed):
            with open(mac_datafeed, "r") as mac_file:
                for mac in mac_file:
                    mac = mac.replace("-", ":") # Just easier to assume dashes needs to be replaced with colons
                    try:
                        matching_mac = re.search(mac_regex, mac)
                        mac_lookup(matching_mac.group())
                    except AttributeError as err:
                        print(f"{mac} \t\t**MAC address not following IEEE format (seperated by colon/hiphens)**")
        else:
            print(f"The path provided does not exists: {args.path}. Please try again...")

if __name__ == "__main__":
    main()