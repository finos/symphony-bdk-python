#!/usr/bin/env bash

template_dir=`pwd`
project_root=$template_dir/..

echo $template_dir

generate_files() {
  file_url=$1
  file_name=${file_url##*/}
  name=$2

  # download and generate files
  cd $template_dir
  curl $file_url -o $file_name
  java -jar openapi-generator-cli.jar generate -g python -i $file_name --package-name symphony.bdk.gen -o output

  # update api files
  cd $template_dir/output/symphony/bdk/gen/api/
  sed -i ".bak" "s/symphony\.bdk\.gen\.model\./symphony\.bdk\.gen\.${name}_model\./g" *.py
  sed -i ".bak" "s/ api\./ ${name}_api\./g" *.py
  rm __init__.py  # we don't care about __init__.py files
  cp *.py $project_root/symphony/bdk/gen/${name}_api

  # update model files
  cd $template_dir/output/symphony/bdk/gen/model/
  sed -i ".bak" "s/symphony\.bdk\.gen\.model\./symphony\.bdk\.gen\.${name}_model\./g" *.py
  sed -i ".bak" "s/model /${name}_model /g" *.py
  rm __init__.py  # we don't care about __init__.py files
  cp *.py $project_root/symphony/bdk/gen/${name}_model

  cd $template_dir
  rm -r output
  rm $file_name
}

generate_files https://raw.githubusercontent.com/symphonyoss/symphony-api-spec/7e3b6d0503a3f7875fc36fee01dd0d93ff4ceb20/agent/agent-api-public.yaml agent
generate_files https://raw.githubusercontent.com/symphonyoss/symphony-api-spec/7e3b6d0503a3f7875fc36fee01dd0d93ff4ceb20/authenticator/authenticator-api-public-deprecated.yaml auth
generate_files https://raw.githubusercontent.com/symphonyoss/symphony-api-spec/7e3b6d0503a3f7875fc36fee01dd0d93ff4ceb20/login/login-api-public.yaml login
generate_files https://raw.githubusercontent.com/symphonyoss/symphony-api-spec/7e3b6d0503a3f7875fc36fee01dd0d93ff4ceb20/pod/pod-api-public.yaml pod

curl https://raw.githubusercontent.com/finos/symphony-api-spec/7e3b6d0503a3f7875fc36fee01dd0d93ff4ceb20/profile-manager/symphony-common-definitions.yaml -o symphony-common-definitions.yaml
generate_files https://raw.githubusercontent.com/finos/symphony-api-spec/7e3b6d0503a3f7875fc36fee01dd0d93ff4ceb20/profile-manager/profile-manager-api.yaml profile_manager
