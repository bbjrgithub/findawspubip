#!/usr/bin/env python3
#
# #########################################################################
# findawspubip.py: Searches all regions in an AWS account for a specified public IP.
#
# Usage:  $ ./findawspubip.py <public IP>
#
# Example:  $ ./findawspubip.py 52.9.137.45
#
#           Searching for IP in: us-west-1
#
#           IP 52.9.137.45 Found:
#
#           ENI: eni-0c24eddb53e82f719, PrivateIP: 172.31.12.247, PublicIP: 52.9.137.45
#
#
# Copyright (C) 2020 Bill Banks Jr
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# #########################################################################


import boto3
import argparse
import pprint
import re

IP = 0
region_names = []
eni_info_per_region = []


# Parse the command line options

def parse_command_line():
    global IP
    cmdline_parser = argparse.ArgumentParser()
    cmdline_parser.add_argument("ip_address", help="IP address to search for")
    IP = cmdline_parser.parse_args()

    # Use in regular expression to validate the entered IP address

    regex_for_IP = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
                   25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
                   25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
                   25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$'''

    if (re.search(regex_for_IP, IP.ip_address)):
       get_list_of_regions()

    else:
        print(f"\"{IP.ip_address}\" is an invalid IP address")
        raise SystemExit


# Get list of the regions that are valid for the account

def get_list_of_regions():
    ec2_client = boto3.client('ec2')
    data_on_all_regions = ec2_client.describe_regions()
    global region_names
    
    for each_region in data_on_all_regions['Regions']:
        region_names.append(each_region['RegionName'])


# Search the list of regions for the IP

def search_regions_for_IP():
    global region_names
    global IP

    # Print account number
    sts_client = boto3.client("sts")
    account_id = sts_client.get_caller_identity()["Account"]
    print(f"Searching account {account_id}\n")

    for each_region_name in region_names:
        session_for_region = boto3.session.Session(region_name=each_region_name)
        network_intefaces = session_for_region.client('ec2')
        network_intefaces_paginator = network_intefaces.get_paginator('describe_network_interfaces')
        pages = network_intefaces_paginator.paginate()

        print('Searching for IP in:', each_region_name)

        for page in pages:
            for interface in page['NetworkInterfaces']:

                # If the ENI has an Association then it has a public IP
                if "Association" in interface:

                    # If the Association's public IP matches the one that is being searched for then the IP has been found 
                    if IP.ip_address == interface['Association']['PublicIp']:
                       print(f"\nIP {IP.ip_address} Found:")
                       print(f"\nENI: {interface['NetworkInterfaceId']}, PrivateIP: {interface['PrivateIpAddress']}, PublicIP: {interface['Association']['PublicIp']}\n")

                       break
            else:
                continue
            break

        else:
            continue
        break



parse_command_line()
search_regions_for_IP()
