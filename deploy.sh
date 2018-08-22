#!/usr/bin/env bash

./manage_assets.py buildqa tester1 test "$(date '+%Y-%m-%d')"
if [ $? == true ]; then
   echo "Release already exists - will delete all old assets"; 
   ./manage_assets.py buildqa tester1 "$(date '+%Y-%m-%d')" delete all;
else
   echo "Making new release";
   hub release create -m "$(date +'%Y-%m-%d')" "$(date +'%Y-%m-%d')";
fi

