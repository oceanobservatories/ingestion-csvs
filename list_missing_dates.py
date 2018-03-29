import sys

import requests
import json


def get_refdes_list(server):
    """
    Get list of reference designators that are available on the server
    """
    http = ''.join(['http://', server, ':12576/sensor/inv/'])
    r = requests.get(http)
    refdes_list = []
    
    for site in r.json():
        site_http = http + site + '/'
        site_node = requests.get(site_http)
        
        for node in site_node.json():
            node_http = site_http + node + '/'
            site_node_inst = requests.get(node_http)
            
            for inst in site_node_inst.json():
                refdes_list.append(site + '-' + node + '-' + inst)
    return refdes_list


def get_missing_data_list(refdes, server):
    """ 
    Get list of missing dates
    """
    http = ''.join(['http://', server, '.intra.oceanobservatories.org:9000/available/', refdes])
    http = http.replace('\n', '')
    r = requests.get(http)
    data = r.json()
    missing_data_list = []
    
    if len(data['availability']) > 1:
        for start_date, status, end_date in data['availability'][1]['data']:
            if status == 'Missing':
                missing_data_list.append((start_date, end_date))

        if missing_data_list:
            return missing_data_list