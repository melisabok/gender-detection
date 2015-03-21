#!/usr/bin/env python2.6
#-*- coding:utf-8 -*-

import csv

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, first_line_is_header=False, **kwargs):
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect,
                            **kwargs)
    if first_line_is_header:
        csv_reader.next()
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')