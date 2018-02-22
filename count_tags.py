# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 23:00:37 2017

@author: SSUHAILA
"""

#to find number of tags inside this OSM file

def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag in tags: 
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags
    
print(count_tags(OSM_FILE))