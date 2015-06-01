#!/usr/bin/python

import sys
import os
import demon
import signal
import csv
import os
import io
from time import time
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DatabaseError
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Sequence
from datetime import datetime
from urllib import unquote_plus
from urlparse import urlparse
from optparse import OptionParser

path = "/home/eis/"
with open('rekening.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='"')
    rekening = {}
    for row in spamreader:
        is_text =False
        rek = nama = ''
        c = list(row)
        for i  in range(len(c)):
            if c[i].isdigit():
                if is_text:
                    rekening[rek] = nama
                    rek = nama = ''
                    is_text = False
                rek = '.'.join([rek,row[i]])
            else:
                is_text = True
                nama = ' '.join([nama,row[i]])

writer = csv.writer(open('result.csv', 'wb'))
for key, value in rekening.items():
   writer.writerow([key, value])            