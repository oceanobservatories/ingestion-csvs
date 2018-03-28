import sys
import requests, json


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
        for i in data['availability'][1]['data']:
            if i[1] == "Missing":
                startDate = i[0]
                endDate = i[2]
                missing_data_list.append((startDate, endDate))
                
        if len(missing_data_list) < 1:
            return None
        else:
            return missing_data_list