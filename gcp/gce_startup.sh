#!/bin/bash
# GCE startup script
set -v

# get project id
PROJECTID=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")

# add user for application
useradd -m -d /home/olivaw olivaw

# fetch the source
export HOME=/root
git config --global credential.helper gcloud.sh
rm -rf ./olivaw_tmp
git clone https://source.developers.google.com/p/${PROJECTID}/r/${PROJECTID} ./olivaw_tmp
mv ./olivaw_tmp/* ./olivaw_tmp/.* /home/olivaw/
chown -R olivaw:olivaw /home/olivaw

# run bootstrap script
cd /home/olivaw
( "./gcp/gce_bootstrap.sh" )
