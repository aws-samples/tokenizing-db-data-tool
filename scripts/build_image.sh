#!/bin/bash

CMDNAME=`basename $0`

if [ $# -ne 1 ]; then
  echo "Usage: $CMDNAME [preprd|prd]" 1>&2
  exit 1
fi

if [ "$1" = "preprd" ]; then
    export AWS_PROFILE=demo-preprd
elif [ "$1" = "prd" ]; then
    export AWS_PROFILE=demo-prd
else
  echo "Usage: $CMDNAME [preprd|prd]" 1>&2
  exit 1
fi
name=db-tokenization
awsAccount=$(aws sts get-caller-identity --output text --query Account)

aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin $awsAccount.dkr.ecr.ap-southeast-1.amazonaws.com
docker buildx build --platform=linux/amd64 -t $name .
docker tag $name:latest $awsAccount.dkr.ecr.ap-southeast-1.amazonaws.com/$name:latest
docker push $awsAccount.dkr.ecr.ap-southeast-1.amazonaws.com/$name:latest
