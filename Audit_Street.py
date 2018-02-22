# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 22:52:04 2017

@author: SSUHAILA
"""

"""
Audit and map the street name to the correct name
Code adapted from Udacity Quiz 10: Improving Street Names

"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

#OSMFILE = "example.osm"
#Use SAMPLE_FILE
OSM_FILE = "kuala-lumpur_malaysia.osm" 
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Jalan", "Persiaran", "Lorong","Lebuh"]

# UPDATE THIS VARIABLE
mapping = { "Jln": "Jalan",
            "Jln.": "Jalan",
            "jalan": "Jalan",
            "Prsn": "Persiaran",
            "Prsn": "Persiaran",
            "Lrng": "Lorong",
            "Lrng.": "Lorong",
            "lorong": "Lorong",
            "Drive": "Persiaran",
            "Drv": "Persiaran",
            "Drv.": "Persiaran",
            "Lane": "Lorong",
            "Road": "Jalan",
            "Rd": "Jalan",
            "Rd.": "Jalan",
            "Street": "Lebuh",
            "St": "Lebuh",
            "St.": "Lebuh"}


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    #print 'update name', name
    split_name=name.split(' ')
    
    for i in split_name:
        if i in mapping:
            name=name.replace(i, str(mapping[i]))
            print 'New name', name

    return name

st_types= audit(OSM_FILE)

#Checking the new street names 

for st_type, ways in st_types.iteritems():
    for name in ways:
        corrected_name = update_name(name, mapping)
        print name, "to", corrected_name
