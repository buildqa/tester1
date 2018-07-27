#!/usr/bin/env python

import sys, os, re
import commands

debug = True
# debug = False

if debug: print("argv = %s") % sys.argv

def main():

   asset_action = ""

   # <prog> <git userid> <repo name> <release tag> <file name of asset to replace/add in release> <action={delete,add}>
   # <prog>    buildqa      tester1   2017-07-26                  darwin.tgz                            delete
   # <prog>    buildqa      tester1   2017-07-26                  darwin.tgz                             add
   usage_msg = "$ %s <git userid> <repo name> <release tag> <file name of asset to replace/add in release> <action={delete,add}>" % (sys.argv[0])

   if not len(sys.argv) == 6:
      print("Insufficient arguments provided.")
      print("USAGE: %s") % usage_msg
   else:
      git_userid = sys.argv[1]
      git_repo_name = sys.argv[2]
      release_tag = sys.argv[3]
      asset_name = sys.argv[4]
      asset_action = sys.argv[5]

   if not os.environ['GITHUB_TOKEN']:
      # Note that pushing a file that contains a (raw) personal access or OAUTH token will cause it to be revoked by github
      print("GITHUB_TOKEN for curl access must be defined in environment and entered in developer settings on github")
      sys.exit(1)
   else:
      github_token = os.environ['GITHUB_TOKEN']

   if (asset_action != "delete") or (asset_action != "add"):
      print("Must provide argument for asset action as 'delete' or 'add'.")


   if (asset_action == "delete"):

      # get description of release and all included assets (files) as currently posted on github via rev3 API
      #
      # curl -sH 'Authorization: token <github token>' https://api.github.com/repos/buildqa/tester1/releases/tags/2018-07-26
      curl_query_cmd = "curl -sH " + "'" + "Authorization: token " + github_token + "'" + " " + "https://api.github.com/repos/" + git_userid + "/" + git_repo_name + "/releases/tags/" + release_tag
      curl_query_output = run_cmd(curl_query_cmd,False,True) 

      # sys.exit(0)

      if debug: print("Searching for asset URL for file %s") % asset_name

      marker_1 = False
      marker_2 = False
      marker_3 = False

      # Example: pattern of sequential lines to match in api output via curl for file darwin.tgz, asset in release 2018-07-25
      #
      # "url": "https://api.github.com/repos/buildqa/tester1/releases/assets/8018113",
      # "id:" 8018113,
      # "node_id:" "MDEyOlJlbGVhc2VBc3NldDgwMTQ3NTQ=",
      # "name:" "darwin.tgz",

      asset_entry = ""
      asset_url = ""
      cnt_asset = 0
      cnt = 1

      for newline in curl_query_output.split('\n'):
         # remove double quotes
         line = re.sub(r'"','',newline)
         if debug: print("%s: %s") % (cnt,line.strip('\r\n'))

         if re.match(r'^[ ]*url: ',line):
            cnt_url = cnt
            asset_url = re.sub(r'^.*url: ','',line)
            marker_1 = True
            if debug: print("marker 1 is TRUE")

         if marker_1 and re.match(r'^[ ]*id: ',line):
            cnt_id = cnt
            asset_id = re.sub(r'^.*id: ','',line)
            marker_2 = True
            if debug: print("marker 2 is TRUE")

         if marker_1 and marker_2 and re.match(r'^[ ]*node_id: ',line):
            marker_3 = True
            if debug: print("marker 3 is TRUE")

         if marker_1 and marker_2 and marker_3 and re.match(r'^[ ]*name: ',line) and re.search(asset_name,line):
            cnt_asset = cnt
            asset_entry = re.sub(r'^.*: ','',line)
            if debug: print("Found asset")
            break

         cnt += 1

      if (cnt_asset == 0):
         if debug: print("No URL found to match file %s") % asset_name
         # sys.exit(1)
         sys.exit(0)

      if asset_url and (cnt_asset != 0):
         url_line = re.sub(r'^[ ]*url: ','',asset_url.strip('\n\r'))
         if debug: print("url is %s at line %s FOR asset %s at line %s") % (url_line, cnt_url, re.sub(',','',asset_entry.strip('\n\r')), cnt_asset)

         # delete the asset from the release with its asset URL (which contains its asset ID)
         #
         # curl '' -X DELETE -H 'Authorization: token <github token>' 'https://api.github.com/repos/buildqa/tester1/releases/assets/8018113'
         curl_delete_cmd = "curl " + "''" + " -X DELETE -H " + "'" + "Authorization: token " + github_token + "'" + " " + "'" + url_line.strip(',') + "'"
         curl_delete_output = run_cmd(curl_delete_cmd,False,True) 

   elif (asset_action == "add"):

      if debug: print("upload file %s") % asset_name

      # get upload URL from release info
      # curl -sH 'Authorization: token <github token>' https://api.github.com/repos/buildqa/tester1/releases/tags/2018727 | grep upload_url
      #
      # result looks something like below, so get correct filed, remove double quotes, commas
      # "upload_url": "https://uploads.github.com/repos/buildqa/tester1/releases/12129991/assets{?name,label}",

      curl_geturl_cmd = "curl -sH " + "'" + "Authorization: token " + github_token + "'" + " " + "https://api.github.com/repos/" + git_userid + "/" + git_repo_name + "/releases/tags/" + release_tag + " | grep upload_url | awk '{print $2}' | sed 's;\";;g' | sed 's;,;;g' "
      if debug: print("curl_geturl_cmd = %s") % curl_geturl_cmd

      curl_rawurl_output = run_cmd(curl_geturl_cmd,False,True) 
      if debug: print("curl_rawurl_output = %s") % curl_rawurl_output

      # change "assets{?name,label}" to "assets?name=foo.tgz" to upload file foo.tgz
      curl_upload_url_1 = re.sub(r'[{}]','',curl_rawurl_output)
      if debug: print("curl_upload_url_1 = %s") % curl_upload_url_1

      name_string = "name=" + asset_name
      curl_upload_url_2 = re.sub('name?label',name_string,curl_upload_url_1)
      if debug: print("curl_upload_url_2 = %s") % curl_upload_url_2

      # Use upload URL to form curl command to upload file
      #
      # curl '' --data-binary @./foo2.tgz -H 'Authorization: token <github token>' -H 'Content-Type: application/octet-stream' 'https://uploads.github.com/repos/buildqa/tester1/releases/12129991/assets?name=foo2.tgz'

      # note use of hardcoded ./install path prefix - assume uploads under <top of tree>/install

      curl_upload_cmd = "curl " + "''" + " --data-binary @./install/" + asset_name + " -H " + "'" + "Authorization: token " + github_token + "'" + " -H " + "'" + "Content-Type: application/octet-stream" + "'" + " " + "'" + curl_upload_url_2 + "'"
      if debug: print("curl_upload_cmd = %s") % curl_upload_cmd

      curl_upload_output = run_cmd(curl_upload_cmd,False,True) 
      if debug: print("curl_upload_output = %s") % curl_upload_output

      sys.exit(0)




def run_cmd(cmd,fake=False,report_cmd=False):
   if not fake:
      if debug: print "Running cmd: %s" % (cmd)
      cmd_ret = commands.getstatusoutput(cmd)
      if cmd_ret[0] == 0:
         if (report_cmd): print "command succeeded: %s" % (cmd)
         return cmd_ret[1]
      else:
         if (report_cmd): print "*** command failed: %s" % (cmd)
         sys.exit(1)
         # return True
         return False
   else:
      print "+++ Would exec: %s\n" % (cmd)
      return True


if __name__ == "__main__":
   main()
