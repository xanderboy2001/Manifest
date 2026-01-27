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



source "${__dir}/stow_logic.sh"

if command -v gum >/dev/null 2>&1; then
		TUI_CMD=gum
else command -v dialog >/dev/null 2>&1; then
		TUI_CMD=dialog
fi

if ! command -v "$TUI_CMD" >/dev/null 2>&1; then
		echo "${RED}ERROR: gum or dialog is required!${ENDCOLOR}"
fi

init_ui() {
		local m_path=$(get_opt manifest_path)
		if [ ! -d "$m_path" ]; then
				if [ $TUI_CMD = 'gum' ]; then
						gum log --structured --level debug "${m_path} not found!"
						gum input --prompt "Enter path for dotfiles to live: " --prompt "$m_path" --value "$m_path"

				fi
		fi
}

choose_config_gum() {
		echo $(list_configs | gum choose --header "Choose a config:")
}
