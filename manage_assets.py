#!/usr/bin/env python

import sys, os, re
import commands

debug = True
# debug = False

if debug: print("argv = %s") % sys.argv

if not os.environ['GITHUB_TOKEN']:
   # Note that pushing a file that contains a (raw) personal access or OAUTH token will cause it to be revoked by github
   print("GITHUB_TOKEN for curl access must be defined in environment and entered in developer settings on github")
   sys.exit(1)
else:
   github_token = os.environ['GITHUB_TOKEN']


def main():

   git_userid = ''
   git_repo_name = ''
   release_tag = ''
   asset_action = ''
   asset_name = ''

   # manage_assets.py buildqa tester1 untagged-b6410855dff21b5deabb add darwin_2018-08-06_125953.tgz
   # <prog> <git userid> <repo name> <release tag> <action={delete,add}> <optional name of specific asset to delete or add>
   usage_msg = "$ %s <git userid> <repo name> <release tag> <action={delete,add}> <asset name to replace/add in release | \"all\" to delete all assets > " % (sys.argv[0])

   if not len(sys.argv) != 5:
      print("Insufficient arguments provided.")
      print("USAGE: %s") % usage_msg
   else:
      git_userid = sys.argv[1]
      git_repo_name = sys.argv[2]
      release_tag = sys.argv[3]
      asset_action = sys.argv[4]
      asset_name = sys.argv[5]

   if (asset_action != "delete") and (asset_action != "add"):
      print("Must provide argument for asset action as 'delete' or 'add'.")
      sys.exit(1)
   if (asset_action != "add") and not asset_name:
      print("Must provide a file (asset name) to add to the release with action 'add'.")
      sys.exit(1)

   # add named asset from command line
   if (asset_action == "add") and (asset_name):
      print("Should add asset %s to release %s") % (asset_name,release_tag)
      add_asset(asset_name,git_userid,git_repo_name,release_tag)
      sys.exit(0)

   # delete a single or all assets from a release
   release_assets = get_assets(release_tag,git_userid,git_repo_name)

   if release_assets:
      key_list = list(release_assets)
      if debug: print("key_list = %s") % key_list
      cnt = 1
      for asset in key_list:
         if debug: print("Asset %s has URL %s") % (asset,release_assets[asset])
         asset_url = release_assets[asset]
         # delete with asset "all" will delete any assets found in the release
         # (assets should be deleted before the tag for the release is deleted)
         if (asset_action == "delete") and (asset_name == "all"):
            print("Should delete asset %s of %s from release %s: %s") % (cnt,len(key_list),release_tag,asset)
            delete_asset(asset,asset_url)
            cnt += 1

      if (asset_action == "delete") and (asset_name != "all"):
         # delete named asset from command line  
         if asset_name in key_list:
            asset_url = release_assets[asset_name]
            print("Should delete argument asset %s from release %s") % (asset_name,release_tag)
            delete_asset(asset_name,asset_url)
         else:
            print("No asset %s listed to delete for release tag %s... exitting") % (asset_name,release_tag)
            sys.exit(0)

   else:
      print("No assets listed for release tag %s... exitting") % (release_tag)
 
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


def delete_asset(asset,url):

   if debug: print("Asset %s to delete has URL %s") % (re.sub(',','',asset.strip('\n\r')), url)

   # delete the asset from the release with its asset URL (which contains its asset ID)
   #
   # curl '' -X DELETE -H 'Authorization: token <github token>' 'https://api.github.com/repos/buildqa/tester1/releases/assets/8018113'
   curl_delete_cmd = "curl " + "''" + " -X DELETE -H " + "'" + "Authorization: token " + github_token + "'" + " " + "'" + url.strip(',') + "'"
   curl_delete_output = run_cmd(curl_delete_cmd,False,True) 
   # curl_delete_output = run_cmd(curl_delete_cmd,True,True) 



def add_asset(asset,userid,repo_name,tag):

   # get upload URL from release info
   # curl -sH 'Authorization: token <github token>' https://api.github.com/repos/buildqa/tester1/releases/tags/2018727 | grep upload_url
   #
   # result looks something like below, so get correct filed, remove double quotes, commas
   # "upload_url": "https://uploads.github.com/repos/buildqa/tester1/releases/12129991/assets{?name,label}",

   curl_geturl_cmd = "curl -sH " + "'" + "Authorization: token " + github_token + "'" + " " + "https://api.github.com/repos/" + userid + "/" + repo_name + "/releases/tags/" + tag + " | grep upload_url | awk '{print $2}' | sed 's;\";;g' | sed 's;,;;g' "
   if debug: print("curl_geturl_cmd = %s") % curl_geturl_cmd

   curl_rawurl_output = run_cmd(curl_geturl_cmd,False,True) 
   if debug: print("curl_rawurl_output = %s") % curl_rawurl_output

   # change "assets{?name,label}" to "assets?name=foo.tgz" to upload file foo.tgz
   curl_upload_url_1 = re.sub(r'[{}]','',curl_rawurl_output)
   if debug: print("curl_upload_url_1 = %s") % curl_upload_url_1

   name_string = "name=" + asset
   curl_upload_url_2 = re.sub('name?label',name_string,curl_upload_url_1)
   if debug: print("curl_upload_url_2 = %s") % curl_upload_url_2

   # Use upload URL to form curl command to upload file
   #
   # curl '' --data-binary @./foo2.tgz -H 'Authorization: token <github token>' -H 'Content-Type: application/octet-stream' 'https://uploads.github.com/repos/buildqa/tester1/releases/12129991/assets?name=foo2.tgz'

   # note use of hardcoded ./install path prefix - assume uploads under <top of tree>/install

   curl_upload_cmd = "curl " + "''" + " --data-binary @./install/" + asset + " -H " + "'" + "Authorization: token " + github_token + "'" + " -H " + "'" + "Content-Type: application/octet-stream" + "'" + " " + "'" + curl_upload_url_2 + "'"
   if debug: print("curl_upload_cmd = %s") % curl_upload_cmd

   curl_upload_output = run_cmd(curl_upload_cmd,False,True) 
   # curl_upload_output = run_cmd(curl_upload_cmd,True,True) 
   if debug: print("curl_upload_output = %s") % curl_upload_output



def get_assets(tag,userid,repo_name):

   # get description of release and all included assets (files) as currently posted on github via rev3 API
   #
   # curl -sH 'Authorization: token <github token>' https://api.github.com/repos/buildqa/tester1/releases/tags/2018-07-26
   curl_query_cmd = "curl -sH " + "'" + "Authorization: token " + github_token + "'" + " " + "https://api.github.com/repos/" + userid + "/" + repo_name + "/releases/tags/" + tag
   curl_query_output = run_cmd(curl_query_cmd,False,True) 

   # sys.exit(0)

   marker_0 = False
   marker_1 = False
   marker_2 = False
   marker_3 = False

   # Example: pattern of sequential lines to match in api output via curl for file darwin.tgz, asset in release 2018-07-25
   #
   # "url": "https://api.github.com/repos/buildqa/tester1/releases/assets/8018113",
   # "id:" 8018113,
   # "node_id:" "MDEyOlJlbGVhc2VBc3NldDgwMTQ3NTQ=",
   # "name:" "darwin.tgz",

   asset_hash = {}
   asset_entry = ""
   asset_url = ""
   cnt_asset = 0
   cnt = 0

   for newline in curl_query_output.split('\n'):
      cnt += 1
      # remove double quotes
      line = re.sub(r'"','',newline)
      if debug: print("%s: %s") % (cnt,line.strip('\r\n'))

      # first get to the assets section of the output
      if re.match(r'^[ ]*assets: ',line):
         cnt_url = cnt
         marker_0 = True
         if debug: print("marker 0 is TRUE")

      # then any entries for assets should follow
      if marker_0 and re.match(r'^[ ]*url: ',line):
         cnt_url = cnt
         asset_url = re.sub(r'^.*url: ','',line)
         marker_1 = True
         if debug: print("marker 1 is TRUE")
  
      if marker_0 and marker_1 and re.match(r'^[ ]*id: ',line):
         cnt_id = cnt
         asset_id = re.sub(r'^.*id: ','',line)
         marker_2 = True
         if debug: print("marker 2 is TRUE")

      if marker_0 and marker_1 and marker_2 and re.match(r'^[ ]*node_id: ',line):
         marker_3 = True
         if debug: print("marker 3 is TRUE")

      if marker_0 and marker_1 and marker_2 and marker_3 and re.match(r'^[ ]*name: ',line):
         cnt_asset = cnt
         raw_asset_entry = re.sub(r'^[ ]*name: ','',line)
         asset_entry = re.sub(r',$','',raw_asset_entry)
         if debug: print("Found asset _%s_") % asset_entry

         url_line = re.sub(r'^[ ]*url: ','',asset_url.strip('\n\r'))
         if debug: print("url is %s at line %s FOR asset %s at line %s") % (url_line, cnt_url, re.sub(',','',asset_entry.strip('\n\r')), cnt_asset)
         # asset name is key and value is URL (e.g., to be used as arg if want to delete
         asset_hash[asset_entry] = url_line 
         # break

   if (cnt_asset == 0):
      if debug: print("No assets found to match release tag %s") % tag

   return asset_hash




if __name__ == "__main__":
   main()
