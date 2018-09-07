# tester1

The idea is to have a daily build with the tag and release name using a YEAR-MONTH-DAY timestamp.  There may be however
many builds as needed done per day, but the most recent build and its contents should supercede any previous builds
(done on that day) under the release YEAR-MO-DAY.

If the release and tag for a given YEAR-MO_DAY does not exist, they will be created, and the build assets are
uploaded if the Travis build succeeds.  The .travis.yml script uses the "after success" stage and NOT the
"before deploy" and "deploy" stages to do this.  The deploy stages are not used because the commit must be
tagged in order for the deploy stage to not automatically create a release and tag using a hash thereby
cluttering up the release and tag entries on the github web page with unwanted/duplicate entries.

Or, for the "before deploy" stage to do any work, the "deploy" stage must be used, and the desired entry
for the deploy stage would be something like the following IN ORDER NOTE TO CREATE A TAG USING A GENERATED
HASH,

deploy:
   provider: releases
   api_key: $GITHUB_TOKEN
   overwrite: true
   script: files=(./install/darwin_2018*.tgz) && ./manage_assets.py buildqa tester1 "$(date '+%Y-%m-%d')" add $files
   skip_cleanup: true
   on:
     tags: true

So a "deploy.sh" script is run from the "after success" stage which in turn utilizes "manage_assets.py" to
delete or upload assets to the release.  The deploy.sh script is used as follows,

./deploy.sh <add,delete> [<release name>]
Must provide action as first argument <add,delete> followed by optional release name [<release name>]
The release name defaults to the current year-month-day without a timestamp, e.g., 2018-09-07
=> ./deploy.sh add 2018-09-07
=> ./deploy.sh delete 2018-09-07

When deploy.sh deletes a release it does the following (if the release already exists), e.g., updating the daily build:

1) find all the release assets and delete them, i.e., for this project the single file darwin_2018-09-06_060726.tgz 
   will be deleted - previously uploaded by "deploy.sh add" via manage_assets.py when the release was created.

manage_asssets.py is used to delete individual assets by their ID number using curl commands

2) use the hub/github release command to delete the release

hub release delete <release name>

...now the tag and the associated default source file archives created for the release still remain...

3) use the git tag command to delete the tag (which will also delete the source file archives)

git push --delete origin \<release name\>


As of this writing a "build" simply creates a tar archive whose contents are not used for anything 
- only the name of the archive is significant as it contains a timestamp
in the form of YEAR-MO-DAY followed by hours minutes seconds in the file name.

So each time a build occurs from a file change on github, then same release with name YEAR-MO-DAY is upadted.  Or you
should see in just a few minutes the name of the tar archive asset it change to reflect the more detailed timestamp
YEAR_MO_DAY_|HR|MIN|SEC|, i.e., the hours minutes seconds entry will be younger each time the tar file asset is 
built and uploaded (to the same release).


The releases.py script looks to prune old releases.  It has a (pre)set count of releases to keep, and deletes any 
(older) releases exceeding the count to save.  In this example, there is only 1 release in the project here,
so the number of releases to keep is set to zero.  It finds the one release, and then deletes it:

% ./releases.py
command succeeded: /usr/local/bin/github-release info -u buildqa -r tester1
Found releases in repo tester1:

release = - 2018-09-07 with tag = 201809072009
value = 2018-09-07
key = 201809072009

releases sorted from oldest to newest = ['201809072009']
There are currently 1 releases
Should remove 1 releases
Removing assets for release with tag 201809072009 and key 2018-09-07
command succeeded: ./manage_assets.py buildqa tester1 2018-09-07 delete all
Removing release 201809072009 and key 2018-09-07
command succeeded: /usr/local/bin/hub release delete 2018-09-07
Removing tag 201809072009 and key 2018-09-07
command succeeded: git push --delete origin 2018-09-07


See the .travis.yml file for top level steps.  Currently this test build has only been setup on the Mac so
the build may fail for linux.

