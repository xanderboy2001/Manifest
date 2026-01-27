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



source "${__dir}/stow_logic.sh"

if command -v gum >/dev/null 2>&1; then
		TUI_CMD=gum
elif command -v dialog >/dev/null 2>&1; then
		TUI_CMD=dialog
else
		echo -e "${RED}ERROR: gum or dialog is required!${ENDCOLOR}"
		return 1
fi

choose_config_gum() {
		echo $(list_configs | gum choose --header "Choose a config:")
}
