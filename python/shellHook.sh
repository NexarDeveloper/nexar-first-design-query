#!/usr/bin/env -S bash -eu
export fish_prompt_prefix='[altium]'

current_dir="$(realpath $(pwd))"
while true
do
  if [[ -f "${current_dir}/.env" ]]
  then
    source "${current_dir}/.env"
  fi

  if [[ "$(dirname ${current_dir})" == "${current_dir}" ]]
  then
	break
  fi
  current_dir="$(dirname $current_dir)"
done
