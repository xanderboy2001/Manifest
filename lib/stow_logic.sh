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
