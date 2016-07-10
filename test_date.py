__author__ = 'gimdongjin'


import datetime
import time
from time import strftime




created_at = datetime.datetime.now()

print created_at

rr = strftime("%y-%m-%d %H:%M:%S")
print rr
print type(rr)
# year = time.strftime('%Y',created_at)
# month = time.strftime('%m',created_at)


#
# print year
# print month
#
# print type(year)
# print type(month)