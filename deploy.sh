#!/usr/bin/env bash -x

# Example,
# $ sh -x deploy.sh 2018-08-22
# with arg as timestamp to be used for release and tag
if [ "$1" == '' ]; then
  # default to current date for making/updating multiple builds on the same day
  date=$(date '+%Y-%m-%d')
else
  date=$1
fi

# This script will effectively flip the state of a github release
# - If the release does not exist, it will create the tag and release by the same name = $date
# $ sh -x deploy.sh <todays date>
# - Subsequently on the next run, since the release exists, all assets found with ID's will be deleted (but not default source archives).
# $ sh -x deploy.sh <todays date>
# Hence this script is the pre-deploy step in .travis.yml

# test if release with $date tag exists
./manage_assets.py buildqa tester1 "$date" test

if [ $? == 0 ]; then
   echo "Release already exists - will delete all old assets"; 

   # Run script to find and delete assets that were explicitly uploaded, but cannot
   # delete the source archives that got created by default when ther release was first made.
   # Apparently the API does not report the source archives as assets with ID numbers
   # hence they cannot be found and deleted via unique ID's (unlike explcitily uploaded assets).
   ./manage_assets.py buildqa tester1 "$date" delete all;

   # Mac:   hub release (via homebrew)
   # Linux: github release
   #
   # This will technically delete the release on github and change the web page display
   # so the tag does not look like a real release, however the default source archives:
   # Source code (zip)
   # Source code (tar.gz)
   # will remain (see above comments).
   #
   # If you subsequently run this script again with the deletedd release/tag name, the git api will in fact
   # report that it does not exist, and it will "resurrect" the release with the old source archives.
   # Twisted and evil the API is with the dark side >;-O
   #   
   # Comments on stackoverflow seem to indicate source archives can only be deleted on the paid version of github ??
   # https://stackoverflow.com/questions/45240336/how-to-use-github-release-api-to-make-a-release-without-source-code
   hub release delete "$date"
else
   echo "Making new release";
   # release name the same as tag name
   hub release create -m "$date" "$date";
fi

