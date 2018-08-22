# tester1

The idea is to have a daily build with the tag and release name using a YEAR-MO-DAY timestamp.  There may be however
many builds as needed done per day, but the most recent build and its contents should supercede any previous builds
(done on that day) under the release YEAR-MO-DAY.

If the tag and release for a given YEAR-MO_DAY does not exist, then the tag will be created, and the build assets are
uploaded if the Travis build succeeds.  The .travis.yml script calls manage_assets.py to add and delete assets (built
files) from a release, as well as to create the release.  As of this writing a "build" simply creates a tar archive
whose contents are not used for anything - only the name of the archive is significant as it contains a timestamp
in the form of YEAR-MO-DAY followed by hours minutes seconds in the file name.

So each time a build occurs from a file change on github, then even if the release for YEAR-MO-DAY exists, you should 
see in just a few minutes that the name of the tar archive asset in it change to reflect the current timestamp, i.e., 
the hours minutes seconds entry will be younger each time the tar file asset is built and uploaded to the (same)
release.

To delete a release, the assets must first be deleted and then the tag for the release is deleted.  You can do this 
manually on github.  Scripting the tag delete still needs work; querying releases for their assets, and adding/deleting
assets can all be done via curl commands (manage_assets.py).

Finally, a command to prune release (releases.py) looks to prune old releases.  It has a (pre)set count of releases that
should be kept, and any (older) releases exceeding the count to save will be deleted.  (Assets are deleted for each release
but deleting the tag does not seem to work).

See the .travis.yml file for top level steps.  Currently the git release command may only be avalable on the Mac, so
the build will always fail for linux.

