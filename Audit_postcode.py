# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 00:29:45 2017

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
OSM_FILE = "smaller_kl.osm" 
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
postcode_type_re = re.compile(r'([5-6]){1}') #check the first numeric is 5 or 6

#expected list starts with few KL postcodes
expected = ["50594", "56100", "50505","57000"]



def audit_postcode_type(postcode_types, postcode_name):

    m = postcode_type_re.search(postcode_name)
    if m:
        postcode_found = m.group()
        if postcode_found not in expected:
            postcode_types[postcode_found].add(postcode_name)
    else:
        print 'Invalid Postcode'


def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    postcode_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    audit_postcode_type(postcode_types, tag.attrib['v'])
    osm_file.close()
    return postcode_types


def update_name(name):
    #print 'update name', name
    print len(name)
    if len(name)!=5:
        print 'Invalid Postcode'
        name=name.replace(name, str('NA'))
        print name
        return name

shape_postcode= audit(OSM_FILE)

#Checking the new street names 

for zipcode, ways in shape_postcode.iteritems():
    for name in ways:
        corrected_name = update_name(name)
        print name, "to", corrected_name
