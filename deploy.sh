#!/usr/bin/env bash

# Example,
# $ sh -x deploy.sh add
# $ sh -x deploy.sh add 2018-08-22
# $ sh -x deploy.sh delete
# $ sh -x deploy.sh delete 2018-08-22
# with arg as timestamp to be used for release and tag

action=""
if [ "$1" == '' ]; then
   echo "$0 <add,delete> [<release name>]"
   echo "Must provide action as first argument <add,delete> followed by optional release name [<release name>]"
   echo "The release name defaults to the current year-month-day without a timestamp, e.g., $(date '+%Y-%m-%d')"
   echo "=> $0 add $(date '+%Y-%m-%d')"
   echo "=> $0 delete $(date '+%Y-%m-%d')"
   exit 1
elif [ "$1" == "add" ]; then
   action="add"
elif [ "$1" == "delete" ]; then
   action="delete"
else
   echo "Invalid action"
   exit 1
fi

if [ "$2" == '' ]; then
  # default to current date for making/updating multiple builds on the same day
  rel_name=$(date '+%Y-%m-%d')
else
  rel_name=$2
fi

# test if release with $rel_name tag exists
release_exists="FALSE"
./manage_assets.py buildqa tester1 "$rel_name" test
if [ $? == 0 ]; then
   release_exists="TRUE"
   echo "Release $rel_name already exists"
fi

if [ "$action" == "delete" ]; then
   if [ "$release_exists" == "TRUE" ]; then
      # Run script to find and delete assets that were explicitly uploaded for the release.
      # Then the release is deleted, and then the tag for the release is deleted.  The
      # source archives created by default when ther release was first made are deleted
      # when the tag is removed.
      ./manage_assets.py buildqa tester1 "$rel_name" delete all;

      # delete the release
      hub release delete "$rel_name"

   elif [ "$release_exists" == "FALSE" ]; then
      echo "Git API reports release $rel_name does not exist so nothing to do for action = delete"
   fi
   # always try to delete the tag if release does not exist
   git push --delete origin $rel_name || true

elif [ "$action" == "add" ]; then

   if [ "$release_exists" == "TRUE" ]; then
      echo "Git API reports release $rel_name already exists so nothing to do for action = add"
   elif [ "$release_exists" == "FALSE" ]; then
      echo "Making new release";
      # create the release and tag
      hub release create -m "$rel_name" "$rel_name";
   fi
fi

