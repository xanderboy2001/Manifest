#!/usr/bin/env bash

# Strict settings
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
		set -o errexit
		set -o pipefail
		set -o nounset
fi

# On-the-fly-debugging
[[ -n "${DEBUG:-}" ]] && set -x

# "Magic" variables
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
__base="$(basename "${__file}" .sh)"

# Borrowed from https://paul.af/bash-script-preamble-boilerplate



#CONFIG_DIR="${XDG_CONFIG_HOME}/manifest"
CONFIG_DIR="${__dir}/../config"
CONFIG_FILE="${CONFIG_DIR}/manifest.config"
TEMPLATE_FILE="./default.conf"

# Create config dir if it doesn't exist
[[ ! -d "$CONFIG_DIR" ]] && mkdir -p "$CONFIG_DIR"

init() {
		[[ ! -f "$CONFIG_FILE" ]] && cp "$TEMPLATE_FILE" "$CONFIG_FILE"
}

get_opt() {
		local key="$1"
		local val
		val=$(grep "^${key}=" "$CONFIG_FILE" | cut -d'=' -f2- | sed 's/^"//;s/"$//') || return 0
		echo "$val"
}

set_opt() {
		local key="$1"
		local value="$2"
		
		if grep -q "^${key}=" "$CONFIG_FILE"; then
				# using '|' delimiter in sed in case value contains slashes
				sed -i "s|^{key}=.*|${key}=\"${value}\"|" "$CONFIG_FILE"
		else
				echo "${key}=\"${value}\"" >> "$CONFIG_FILE"
		fi
}

init
