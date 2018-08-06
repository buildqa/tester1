#!/usr/bin/env python

import sys, os, re
import platform, commands, operator

repo = "tester1"
uid = "buildqa"
# releases_max = 10  # max number of most recent releases to keep on github
releases_max = 28  # max number of most recent releases to keep on github
debug = True
# debug = False

platform = platform.system()

def main():

   if (platform == "Darwin"):
      # from homebrew on Mac
      github_stat_binary = "/usr/local/bin/github-release"
      github_release_binary = "/usr/local/bin/hub"
   elif (platform == "Linux"):
      github_release_binary = "FIX_ME"
      github_stat_binary = "FIX_ME"
   else:
      print "Unrecognized platform = %s" % (platform)
      sys.exit(1)

   if not os.path.isfile(github_stat_binary):
      print "cannot stat github-stat cmd %s" % (github_stat_binary)
      sys.exit(1)
   if not os.path.isfile(github_release_binary):
      print "cannot stat github-release cmd %s" % (github_release_binary)
      sys.exit(1)

   # github-release info -u buildqa -r tester1 
   release_cmd = github_stat_binary + " info -u " + uid + " -r " + repo 
   output = []
   string = run_cmd(release_cmd)
   output = string.splitlines()

   RE_start_releases = re.compile(r'^releases')
   RE_rel_entry = re.compile(r'^- .*name:.*description:.*tagged:')
   RE_dash_tag = re.compile(r'^- ')

   rel_hash = {} 
   date_list = []
   dmy_list = []
   tstamp_list = []
   for line in output:
      if re.match(RE_start_releases,line):
         print "Found releases in repo %s:\n" % (repo)
      if re.match(RE_rel_entry,line):
         # github-release output for a release
         #  - 07.05.2018, name: '', description: '', id: 11799756, tagged: 05/07/2018 at 19:27, published: 05/07/2018 at 19:28, draft: , prerelease: 
         (tag, name, description, git_id, tag_time, publish_time, draft, prerelease) = line.split(',')
         # tagged: 05/07/2018 at 19:27 
         date_list = tag_time.split(' ')
         # 05 07 2018
         dmy_list = date_list[2].split('/') 
         # 19:27  
         tstamp_list = date_list[4].split(':') 
         # year+mo+day+hr+sec = 201805071927
         timestamp_string = dmy_list[2] + dmy_list[1] + dmy_list[0] + tstamp_list[0] + tstamp_list[1]
         if debug: print "release = %s with tag = %s" % (tag,timestamp_string)
         value = re.sub(RE_dash_tag,'',tag)
         if debug: print "value = %s" % (value)
         key = timestamp_string
         if debug: print "key = %s\n" % (key)
         rel_hash[key] = value

   # put keys (dates) into a sorted list
   key_list = []
   key_list = list(rel_hash)
   key_list_sorted = []
   key_list_sorted = sorted(key_list)

   # sort from oldest to newest
   print "releases sorted from oldest to newest = %s" % (key_list_sorted)
   releases_cnt = len(key_list_sorted)
   if debug: print "There are currently %s releases" % (releases_cnt)
   remove_cnt = releases_cnt - releases_max
   if (remove_cnt > 0):
      cnt = 0
      print "Should remove %s releases" % (remove_cnt)
      while (cnt < remove_cnt):
         # get the tag to delete
         key_delete = key_list_sorted[cnt]
         value_delete = rel_hash[key_delete]

         print "Removing assets for release with tag %s and key %s" % (key_delete,value_delete)
         # Before removing release, remove all the assets (we can) for this release via manage_assets.py
         remove_assets_cmd = "./manage_assets.py buildqa tester1 " + value_delete + " delete all"
         run_cmd(remove_assets_cmd)
         # run_cmd(remove_assets_cmd,True,True)

         print "Removing release with tag %s and key %s" % (key_delete,value_delete)
         # github-release delete -u buildqa -r tester1 -t 20180705
         # delete_cmd = github_release_binary + " delete -u " + uid + " -r " + repo + " -t " + value_delete
         delete_cmd = github_release_binary + " release delete " + value_delete
         run_cmd(delete_cmd)
         # run_cmd(delete_cmd,True,True)

         cnt += 1
   else: 
      print "Not more than %s releases to prune: No releases will be deleted." % (releases_max)


def run_cmd(cmd,fake=False,report_cmd=True):
   if not fake:
      cmd_ret = commands.getstatusoutput(cmd)
      if cmd_ret[0] == 0:
         if (report_cmd): print "command succeeded: %s" % (cmd)
         return cmd_ret[1]
      else:
         if (report_cmd): print "*** Error: command failed: %s" % (cmd)
         return False
   else:
      print "+++ Would exec: %s\n" % (cmd)
      return True


if __name__ == '__main__':
   main()
