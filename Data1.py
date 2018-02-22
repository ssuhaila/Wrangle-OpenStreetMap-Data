# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 00:28:57 2017

@author: SSUHAILA
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Preparing Database.

The OSM data that was previously audited will be transfered to tabular format so it can be inserted into SQL database.

Five csv tags are expected from this function. They are: 
1.nodes.csv
2.nodes_tags.csv
3.ways.csv
4.ways_nodes.csv
5.ways_tags.csv

The fields will be created based on the schema file. The audit function in this file will only audited the street name
from the address tag. 
"""
2
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

#sample_name : sample_kl.osm
OSM_PATH = "smaller_kl.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
postcode_type_re = re.compile(r'([5-6]){1}') #making sure the first char begins with a number between 5 to 6

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

#mapping list so the street names will be corrected
expected = ["Jalan", "Persiaran", "Lorong","Lebuh"]

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

#function from audit street name
def update_name(name, mapping):
    split_name=name.split(' ')
    
    for i in split_name:
        if i in mapping:
            print 'To be Updated', i
            name=name.replace(i, str(mapping[i]))
            print 'Updated Name', name

    return name

def update_name_postcode(postcode_name):

    if len(postcode_name)!=5:
        print 'Invalid Postcode'
        name=name.replace(postcode_name, str('NA'))
        return name
    else:
        m = postcode_type_re.search(postcode_name)
        if m:
            postcode_found = m.group()
            if postcode_found not in expected:
                return postcode_name
                

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        
        for i in element.attrib:
            if i in NODE_FIELDS:
                node_attribs[i] = element.attrib[i]

        for child in element:
            node_tag = {}
            
            if LOWER_COLON.match(child.attrib['k']):
                node_tag['type'] = child.attrib['k'].split(':',1)[0]
                node_tag['key'] = child.attrib['k'].split(':',1)[1]
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = child.attrib['v']
                tags.append(node_tag)
                
            elif PROBLEMCHARS.match(child.attrib['k']):
                continue
            else:
                node_tag['type'] = 'regular'
                node_tag['key'] = child.attrib['k']
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = child.attrib['v']
                tags.append(node_tag)
                
        return {'node': node_attribs, 'node_tags': tags}
        
    elif element.tag == 'way':
        for i_way in element.attrib: 
            if i_way in WAY_FIELDS:
                way_attribs[i_way] = element.attrib[i_way]

        position = 0
        for child in element:
            way_tag = {}
            way_node = {}
            
            if child.tag == 'tag':
                #below if condition came from data audit file
                if LOWER_COLON.match(child.attrib['k']) and child.attrib['k'][:5] == "addr:":
                    if child.attrib['k'][5:] == "street":
                        way_tag['type'] = child.attrib['k'].split(':',1)[0]
                        way_tag['key'] = child.attrib['k'].split(':',1)[1]
                        way_tag['id'] = element.attrib['id']                
                        way_tag['value'] = update_name(child.attrib['v'], mapping)
                        tags.append(way_tag)    
                     
                    if child.attrib['k'][5:] == "postcode":
                        way_tag['type'] = child.attrib['k'].split(':',1)[0]
                        way_tag['key'] = child.attrib['k'].split(':',1)[1]
                        way_tag['id'] = element.attrib['id']                
                        way_tag['value'] = update_name_postcode(child.attrib['v'])
                        print 'wau tag postcode', way_tag['value']
                        tags.append(way_tag)   
                        
                elif LOWER_COLON.match(child.attrib['k']):
                    way_tag['type'] = child.attrib['k'].split(':',1)[0]
                    way_tag['key'] = child.attrib['k'].split(':',1)[1]
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = child.attrib['v']
                    tags.append(way_tag)
                    
                elif PROBLEMCHARS.match(child.attrib['k']):
                    continue
                    
                else:
                    way_tag['type'] = 'regular'
                    way_tag['key'] = child.attrib['k']
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = child.attrib['v']
                    tags.append(way_tag)
                    
            elif child.tag == 'nd':
                way_node['id'] = element.attrib['id']
                way_node['node_id'] = child.attrib['ref']
                way_node['position'] = position
                position += 1
                way_nodes.append(way_node)
        
        #print tags
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}



# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
