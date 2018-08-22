#!/usr/bin/env bash -x

./manage_assets.py buildqa tester1 test "$(date '+%Y-%m-%d')"
if [ $? == 0 ]; then
   echo "Release already exists - will delete all old assets"; 
   ./manage_assets.py buildqa tester1 "$(date '+%Y-%m-%d')" delete all;
else
   echo "Making new release";
   hub release create -m "$(date +'%Y-%m-%d')" "$(date +'%Y-%m-%d')";
fi

