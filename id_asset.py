#!/usr/bin/env python

import sys, os, re

# debug = True
debug = False

if debug: print("argv = %s") % sys.argv
curl_output_file = sys.argv[1]
asset_name = sys.argv[2]
if debug: print("Searching for ID for file %s") % asset_name

marker_1 = False
marker_2 = False

# pattern of sequential lines to match
#
# "id:" 8014754,
# "node_id:" "MDEyOlJlbGVhc2VBc3NldDgwMTQ3NTQ=",
# "name:" "darwin.tgz",

FH = open(curl_output_file,'r')
asset_entry = ""
asset_id = ""
cnt_asset = 0
cnt = 1

for newline in FH:
   # get rid of all double quotes
   line = re.sub(r'"','',newline)
   if debug: print("%s: %s") % (cnt,line.strip('\r\n'))
   if re.match(r'^[ ]*id: ',line):
      cnt_id = cnt
      asset_id = re.sub(r'^.*id: ','',line)
      marker_1 = True
      if debug: print("marker 1 is TRUE")

   if marker_1 and re.match(r'^[ ]*node_id: ',line):
      marker_2 = True
      if debug: print("marker 2 is TRUE")

   if marker_1 and marker_2 and re.match(r'^[ ]*name: ',line) and re.search(asset_name,line):
      cnt_asset = cnt
      asset_entry = re.sub(r'^.*: ','',line)
      if debug: print("Found asset")
      break

   cnt += 1

ret_line = re.sub(r'^[ ]*id: ','',asset_id.strip('\n\r'))
if debug: print("id is %s at line %s FOR asset %s at line %s") % (ret_line, cnt_id, re.sub(',','',asset_entry.strip('\n\r')), cnt_asset)

if asset_id and (cnt_asset != 0):
   print("%s") % re.sub(',','',asset_id.strip('\n\r'))
else:
   if debug: print("No ID found to match file %s") % asset_name

