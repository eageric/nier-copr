#!/usr/bin/env bash
set -euo pipefail

log_info() {
    local message="${1}"
    printf '[INFO] %s\n' "${message}"
}

log_error() {
    local message="${1}"
    printf '[ERROR] %s\n' "${message}" >&2
}

print_usage() {
    local script_name="${1}"
    local default_repo="${2}"
    local default_chroot="${3}"
    printf 'Usage: %s [OPTIONS] [PACKAGE...]\n\n' "${script_name}"
    printf 'Options:\n'
    printf '  -r, --repo REPO      COPR repository (default: %s)\n' "${default_repo}"
    printf '  -c, --chroot CHROOT  COPR chroot (default: %s)\n' "${default_chroot}"
    printf '  -f, --force          Build and submit even if version has not changed\n'
    printf '  -n, --dry-run        Update spec files and build SRPMs without submitting to COPR\n'
    printf '  --nowait             Do not wait for COPR build completion\n'
    printf '  -h, --help           Show this help message\n'
}

check_dependencies() {
    local dry_run="${1}"
    local required_cmds=("curl" "jq" "rpmbuild")

    if [[ "${dry_run}" != "true" ]]; then
        required_cmds+=("copr-cli")
    fi

    local cmd
    for cmd in "${required_cmds[@]}"; do
        if ! command -v "${cmd}" >/dev/null 2>&1; then
            log_error "Required command not found: ${cmd}"
            return 1
        fi
    done
    return 0
}

ensure_copr_repo() {
    local copr_repo="${1}"
    local chroot="${2}"
    local project_name="${copr_repo#*/}"

    if copr-cli get-package "${copr_repo}" --name "caprine" >/dev/null 2>&1 || copr-cli list-package-names "${copr_repo}" >/dev/null 2>&1; then
        return 0
    fi

    log_info "Creating COPR repository ${copr_repo} with chroot ${chroot}..."
    copr-cli create "${project_name}" \
        --chroot "${chroot}" \
        --description "Desktop tools and programs repackaged for Fedora"
}

fetch_latest_version() {
    local github_repo="${1}"
    local api_url="https://api.github.com/repos/${github_repo}/releases/latest"
    local response

    if ! response="$(curl -fsSL -H "Accept: application/vnd.github+json" "${api_url}")"; then
        log_error "Failed to query GitHub API for ${github_repo}"
        return 1
    fi

    local tag_name
    tag_name="$(jq -r '.tag_name // empty' <<< "${response}")"
    if [[ -z "${tag_name}" ]]; then
        log_error "No tag_name found in latest release for ${github_repo}"
        return 1
    fi

    local version="${tag_name#v}"
    printf '%s\n' "${version}"
}

read_spec_field() {
    local spec_file="${1}"
    local field_name="${2}"
    local line key value

    while IFS= read -r line; do
        if [[ "${line}" =~ ^([A-Za-z0-9_]+):[[:space:]]*(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            value="${BASH_REMATCH[2]}"
            if [[ "${key}" == "${field_name}" ]]; then
                printf '%s\n' "${value}"
                return 0
            fi
        fi
    done < "${spec_file}"

    return 1
}

read_spec_sources() {
    local spec_file="${1}"
    local version="${2}"
    local line value expanded

    while IFS= read -r line; do
        if [[ "${line}" =~ ^Source[0-9]*:[[:space:]]*(.*)$ ]]; then
            value="${BASH_REMATCH[1]}"
            expanded="${value//%\{version\}/${version}}"
            printf '%s\n' "${expanded}"
        fi
    done < "${spec_file}"
}

update_spec_version() {
    local spec_file="${1}"
    local new_version="${2}"
    local changelog_date
    printf -v changelog_date '%(%a %b %d %Y)T' -1

    local -a updated_lines=()
    local line

    while IFS= read -r line || [[ -n "${line}" ]]; do
        if [[ "${line}" =~ ^(Version:[[:space:]]*).*$ ]]; then
            updated_lines+=("${BASH_REMATCH[1]}${new_version}")
        elif [[ "${line}" =~ ^(Release:[[:space:]]*).*$ ]]; then
            updated_lines+=("${BASH_REMATCH[1]}1%{?dist}")
        elif [[ "${line}" == "%changelog" ]]; then
            updated_lines+=("${line}")
            updated_lines+=("* ${changelog_date} neir-copr - ${new_version}-1")
            updated_lines+=("- Repackage upstream release ${new_version}")
            updated_lines+=("")
        else
            updated_lines+=("${line}")
        fi
    done < "${spec_file}"

    printf '%s\n' "${updated_lines[@]}" > "${spec_file}"
}

download_sources() {
    local spec_file="${1}"
    local version="${2}"
    local sources_dir="${3}"

    mkdir -p "${sources_dir}"

    local -a source_urls=()
    mapfile -t source_urls < <(read_spec_sources "${spec_file}" "${version}")

    local url filename dest_path
    for url in "${source_urls[@]}"; do
        [[ -z "${url}" ]] && continue
        filename="${url##*/}"
        dest_path="${sources_dir}/${filename}"
        if [[ -f "${dest_path}" ]]; then
            log_info "Using cached source: ${filename}"
        else
            log_info "Downloading ${url}..."
            curl -fL --retry 3 -o "${dest_path}.part" "${url}"
            mv "${dest_path}.part" "${dest_path}"
        fi
    done
}

build_srpm() {
    local spec_file="${1}"
    local work_dir="${2}"
    local sources_dir="${work_dir}/SOURCES"
    local srpm_dir="${work_dir}/SRPMS"

    mkdir -p "${sources_dir}" "${srpm_dir}"

    rpmbuild -bs \
        --define "_topdir ${work_dir}" \
        --define "_sourcedir ${sources_dir}" \
        --define "_srcrpmdir ${srpm_dir}" \
        --define "_specdir ${spec_file%/*}" \
        "${spec_file}" >&2

    local -a srpms=("${srpm_dir}"/*.src.rpm)
    if [[ ! -e "${srpms[0]}" ]]; then
        log_error "Failed to locate generated SRPM in ${srpm_dir}"
        return 1
    fi

    printf '%s\n' "${srpms[0]}"
}

submit_to_copr() {
    local copr_repo="${1}"
    local chroot="${2}"
    local srpm_path="${3}"
    local nowait="${4}"
    local -a build_args=("build" "-r" "${chroot}")

    if [[ "${nowait}" == "true" ]]; then
        build_args+=("--nowait")
    fi

    build_args+=("${copr_repo}" "${srpm_path}")

    log_info "Submitting ${srpm_path##*/} to COPR (${copr_repo}, ${chroot})..."
    copr-cli "${build_args[@]}"
}

process_package() {
    local pkg_dir="${1}"
    local build_root="${2}"
    local state_dir="${3}"
    local copr_repo="${4}"
    local chroot="${5}"
    local force_build="${6}"
    local dry_run="${7}"
    local nowait="${8}"

    local conf_file="${pkg_dir}/package.conf"
    if [[ ! -f "${conf_file}" ]]; then
        log_error "Missing package.conf in ${pkg_dir}"
        return 1
    fi

    local GITHUB_REPO=""
    local PACKAGE_NAME=""
    source "${conf_file}"

    if [[ -z "${GITHUB_REPO}" || -z "${PACKAGE_NAME}" ]]; then
        log_error "Invalid package.conf in ${pkg_dir}: GITHUB_REPO and PACKAGE_NAME are required"
        return 1
    fi

    local spec_file="${pkg_dir}/${PACKAGE_NAME}.spec"
    if [[ ! -f "${spec_file}" ]]; then
        log_error "Missing spec file: ${spec_file}"
        return 1
    fi

    log_info "Checking ${PACKAGE_NAME} (${GITHUB_REPO})..."
    local latest_version
    latest_version="$(fetch_latest_version "${GITHUB_REPO}")"

    local spec_version
    spec_version="$(read_spec_field "${spec_file}" "Version")"

    local state_file="${state_dir}/${PACKAGE_NAME}.version"
    local published_version=""
    if [[ -f "${state_file}" ]]; then
        IFS= read -r published_version < "${state_file}" || true
    fi

    if [[ "${spec_version}" != "${latest_version}" ]]; then
        log_info "Updating ${PACKAGE_NAME} spec from ${spec_version} to ${latest_version}"
        update_spec_version "${spec_file}" "${latest_version}"
    fi

    if [[ "${force_build}" != "true" && "${published_version}" == "${latest_version}" ]]; then
        log_info "${PACKAGE_NAME} ${latest_version} is already published to ${copr_repo}; skipping."
        return 0
    fi

    local pkg_work_dir="${build_root}/${PACKAGE_NAME}-${latest_version}"
    rm -rf "${pkg_work_dir}"
    mkdir -p "${pkg_work_dir}"

    download_sources "${spec_file}" "${latest_version}" "${pkg_work_dir}/SOURCES"

    log_info "Building SRPM for ${PACKAGE_NAME} ${latest_version}..."
    local srpm_path
    srpm_path="$(build_srpm "${spec_file}" "${pkg_work_dir}")"
    log_info "Built SRPM: ${srpm_path}"

    if [[ "${dry_run}" == "true" ]]; then
        log_info "Dry-run enabled; skipping COPR upload for ${PACKAGE_NAME} ${latest_version}."
        return 0
    fi

    ensure_copr_repo "${copr_repo}" "${chroot}"
    submit_to_copr "${copr_repo}" "${chroot}" "${srpm_path}" "${nowait}"

    mkdir -p "${state_dir}"
    printf '%s\n' "${latest_version}" > "${state_file}"
    log_info "Recorded ${PACKAGE_NAME} ${latest_version} as published."
}

main() {
    local script_path="${BASH_SOURCE[0]}"
    local script_dir
    script_dir="$(cd -- "${script_path%/*}" && pwd)"

    local copr_repo="${COPR_REPO:-byte0/nier}"
    local chroot="${COPR_CHROOT:-fedora-44-x86_64}"
    local force_build="false"
    local dry_run="false"
    local nowait="false"
    local -a requested_packages=()

    while [[ $# -gt 0 ]]; do
        case "${1}" in
            -r|--repo)
                if [[ $# -lt 2 ]]; then
                    log_error "Missing argument for ${1}"
                    return 1
                fi
                copr_repo="${2}"
                shift 2
                ;;
            -c|--chroot)
                if [[ $# -lt 2 ]]; then
                    log_error "Missing argument for ${1}"
                    return 1
                fi
                chroot="${2}"
                shift 2
                ;;
            -f|--force)
                force_build="true"
                shift
                ;;
            -n|--dry-run)
                dry_run="true"
                shift
                ;;
            --nowait)
                nowait="true"
                shift
                ;;
            -h|--help)
                print_usage "${script_path##*/}" "${copr_repo}" "${chroot}"
                return 0
                ;;
            -*)
                log_error "Unknown option: ${1}"
                print_usage "${script_path##*/}" "${copr_repo}" "${chroot}"
                return 1
                ;;
            *)
                requested_packages+=("${1}")
                shift
                ;;
        esac
    done

    check_dependencies "${dry_run}"

    local packages_root="${script_dir}/packages"
    local build_root="${script_dir}/.build"
    local state_dir="${script_dir}/.state"

    local -a package_dirs=()
    if [[ ${#requested_packages[@]} -gt 0 ]]; then
        local pkg
        for pkg in "${requested_packages[@]}"; do
            if [[ ! -d "${packages_root}/${pkg}" ]]; then
                log_error "Unknown package: ${pkg}"
                return 1
            fi
            package_dirs+=("${packages_root}/${pkg}")
        done
    else
        local dir
        for dir in "${packages_root}"/*; do
            [[ -d "${dir}" ]] && package_dirs+=("${dir}")
        done
    fi

    if [[ ${#package_dirs[@]} -eq 0 ]]; then
        log_error "No packages found in ${packages_root}"
        return 1
    fi

    local pkg_dir
    for pkg_dir in "${package_dirs[@]}"; do
        process_package \
            "${pkg_dir}" \
            "${build_root}" \
            "${state_dir}" \
            "${copr_repo}" \
            "${chroot}" \
            "${force_build}" \
            "${dry_run}" \
            "${nowait}"
    done
}

main "$@"
