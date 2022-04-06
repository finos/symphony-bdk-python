#!/usr/bin/env bash

code_gen_dir=`pwd`
project_root=$code_gen_dir/..
echo $code_gen_dir

commit_hash=2957cb3334a6eff0355f464aa71bbdfb92ae20d2
api_spec_base_url=https://raw.githubusercontent.com/symphonyoss/symphony-api-spec/${commit_hash}
echo $api_spec_base_url

# This function accepts the following parameters (in order):
# - name of the module we want to generate
# - uri of the file to be used for generation
# - uri of the support file needed for the generation
generate_files() {
  name=$1
  file_url=$2
  file_name=${file_url##*/}
  support_file_url=$3
  support_file_name=${support_file_url##*/}


  # download files
  cd $code_gen_dir
  curl $file_url -o $file_name
  if [ ! -z "${support_file_name}" ]
  then
    curl $support_file_url -o $support_file_name
  fi

  # generate files
  java -jar openapi-generator-cli.jar generate -g python -i $file_name --package-name symphony.bdk.gen -o output

  # update api files
  cd $code_gen_dir/output/symphony/bdk/gen/api/
  sed -i ".bak" "s/symphony\.bdk\.gen\.model\./symphony\.bdk\.gen\.${name}_model\./g" *.py
  sed -i ".bak" "s/ api\./ ${name}_api\./g" *.py
  rm __init__.py  # we don't care about __init__.py files
  cp *.py $project_root/symphony/bdk/gen/${name}_api

  # update model files
  cd $code_gen_dir/output/symphony/bdk/gen/model/
  sed -i ".bak" "s/symphony\.bdk\.gen\.model\./symphony\.bdk\.gen\.${name}_model\./g" *.py
  sed -i ".bak" "s/model /${name}_model /g" *.py
  rm __init__.py  # we don't care about __init__.py files
  cp *.py $project_root/symphony/bdk/gen/${name}_model

  # remove downloaded files
  cd $code_gen_dir
  rm -r output
  rm $file_name
  if [ ! -z "${support_file_name}" ]
  then
    rm $support_file_name
  fi
}

generate_files agent ${api_spec_base_url}/agent/agent-api-public-deprecated.yaml
generate_files auth ${api_spec_base_url}/authenticator/authenticator-api-public-deprecated.yaml
generate_files login ${api_spec_base_url}/login/login-api-public.yaml
generate_files pod ${api_spec_base_url}/pod/pod-api-public.yaml

generate_files group ${api_spec_base_url}/profile-manager/profile-manager-api.yaml ${api_spec_base_url}/profile-manager/symphony-common-definitions.yaml
