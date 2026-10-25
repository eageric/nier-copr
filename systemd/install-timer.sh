#!/usr/bin/env bash
set -euo pipefail

install_units() {
    local project_dir="${1}"
    local systemd_user_dir="${2}"
    local user_id="${3}"

    mkdir -p "${systemd_user_dir}"

    local line replaced
    local -a service_lines=()
    while IFS= read -r line || [[ -n "${line}" ]]; do
        replaced="${line//__PROJECT_DIR__/${project_dir}}"
        service_lines+=("${replaced}")
    done < "${project_dir}/systemd/neir-copr.service"

    printf '%s\n' "${service_lines[@]}" > "${systemd_user_dir}/neir-copr.service"
    cp "${project_dir}/systemd/neir-copr.timer" "${systemd_user_dir}/neir-copr.timer"

    export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/${user_id}}"
    systemctl --user daemon-reload
    systemctl --user enable --now neir-copr.timer
    printf '[INFO] Installed and enabled neir-copr.timer in %s\n' "${systemd_user_dir}"
}

main() {
    local script_path="${BASH_SOURCE[0]}"
    local project_dir
    project_dir="$(cd -- "${script_path%/*}/.." && pwd)"
    local config_home="${XDG_CONFIG_HOME:-${HOME}/.config}"
    local systemd_user_dir="${config_home}/systemd/user"

    install_units "${project_dir}" "${systemd_user_dir}" "${UID}"
}

main "$@"
