#!/usr/bin/env bash

# Strict settings
set -o errexit
set -o pipefail
set -o nounset

# On-the-fly-debugging
[[ -n "${DEBUG:-}" ]] && set -x

# "Magic" variables
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
__base="$(basename "${__file}" .sh)"

# Borrowed from https://paul.af/bash-script-preamble-boilerplate



source ${__dir}/colors.sh

if ! command -v stow >/dev/null 2>&1; then
		echo -e "${RED}ERROR: GNU Stow could not be found${ENDCOLOR}"
		exit 1
fi

# Get this from config later
MANIFEST_DEFAULT_PATH="${HOME}/.dotfiles_test"

# accept path and target and perform dry run
dry_run() {
		local m_path=$MANIFEST_DEFAULT_PATH
		local m_target=""

		# loop through arguments and collect variables
		while (( "$#" )); do
				case "$1" in
						--path=*)
								# strip everything up to (and including '=')
								m_path="${1#*=}"
								shift
								;;
						--path|-p)
								# grab second argument
								m_path="$2"
								shift 2
								;;
						--target=*)
								m_target="${1#*=}"
								shift
								;;
						--target|-t)
								m_target="$2"
								shift 2
								;;
						-*)
								echo -e "${RED}ERROR: Unknown option $1${ENDCOLOR}" >&2
								return 1
								;;
						*)
								if [[ -z "$m_path" ]]; then
										m_path="$1"
								else
										m_target="$1"
								fi
								shift
								;;
				esac
		done

		# check if provided path is valid
		if [ ! -d "$m_path" ]; then
				echo -e "${RED}ERROR: '$m_path' is not a valid path!${ENDCOLOR}"
				return 1
		fi

		# check if provided target is valid
		if [ ! -d "${m_path}/${m_target}" ]; then
				echo -e "${RED}ERROR: '$m_target' is not a valid target!${ENDCOLOR}"
				return 1
		fi

		stow --simulate -d "$m_path" "$m_target"
}


# list configs in stow
list_configs() {
		local m_path=$MANIFEST_DEFAULT_PATH
		configs=$(find "$m_path" -mindepth 1 -maxdepth 1 -type d -not -name '.git' -exec basename {} ';')
		echo "$configs"
}
