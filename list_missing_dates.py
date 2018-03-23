import sys
import requests, json

def get_refdes_list():
    http = 'http://uframe-3-test:12576/sensor/inv/'
    r = requests.get(http)
    refdes_json = r.json()
    site_list = []
    refdes_list = []
    
    for item in refdes_json:
        site = item
        site_http = http + item + '/'
        site_node = requests.get(site_http)
        
        for item1 in site_node.json():
            node = item1
            node_http = site_http + item1 + '/'
            site_node_inst = requests.get(node_http)
            
            for item2 in site_node_inst.json():
                inst = item2
                refdes_list.append(site + '-' + node + '-' + inst)
                print site + '-' + node + '-' + inst
    return refdes_list


def get_missing_data_list(refdes):
    http = "http://uframe-3-test.intra.oceanobservatories.org:9000/available/" + refdes
    http = http.replace('\n', '')
    r = requests.get(http)
    data = r.json()
    missing_data_list = []
    
    if len(data['availability']) > 1:
        for i in data['availability'][1]['data']:
            if i[1] == "Missing":
                startDate = i[0].split()[0]
                endDate = i[2].split()[0]
                missing_data_list.append((startDate, endDate))
                
        if len(missing_data_list) < 1:
            return None
        else:
            return missing_data_list
    
    return None