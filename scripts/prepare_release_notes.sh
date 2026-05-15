#!/bin/bash
#********************************************************************
# Script Name:  prepare_release_notes.sh
# Description:  Prepares a release-preparation notes file "a.md" from
#               version.txt and the git history since the last tag.
#
# Location:     llm-shared/scripts/ (mutualized across projects).
#
# Parameters:   $1  optional project directory. When omitted, the
#                   PRJ_DIR environment variable is used, and finally
#                   the current directory.
#
# Usage:        bash <LLM_SHARED_DIR>/scripts/prepare_release_notes.sh
#               (run from <PRJ_DIR>, or pass <PRJ_DIR> as $1)
#
# Reads:        <PRJ_DIR>/version.txt  (first word must be X.Y.Z-SNAPSHOT)
# Writes:       <PRJ_DIR>/a.md
#
# Exit codes:
#   1 - project directory not found or not usable
#   2 - version.txt not found
#   3 - version unreadable from version.txt
#   4 - version.txt version is not a -SNAPSHOT version
#   5 - no git tag found
#   6 - last git tag already matches the snapshot version
#********************************************************************

info()  { echo "Info:  $1"; }
task()  { echo "Task:  $1"; }
ok()    { echo "Ok:    $1"; }
warn()  { echo "Warn:  $1" >&2; }
fatal() { echo "Error: $1" >&2; exit "${2:-1}"; }

# Parse a conventional-commit subject.
# Sets globals: ps_has_colon ps_type ps_scope ps_title
parse_subject() {
  local subject="$1" header
  if [[ "${subject}" != *:* ]]; then
    ps_has_colon=0
    ps_type=""
    ps_scope=""
    ps_title="${subject}"
    return
  fi
  ps_has_colon=1
  header="${subject%%:*}"
  ps_title="${subject#*:}"
  # trim leading whitespace from the title
  ps_title="${ps_title#"${ps_title%%[![:space:]]*}"}"
  if [[ "${header}" == *"("*")"* ]]; then
    ps_type="${header%%(*}"
    ps_scope="${header#*(}"
    ps_scope="${ps_scope%%)*}"
  else
    ps_type="${header}"
    ps_scope=""
  fi
  # normalise type: drop a trailing "!" breaking-change marker and spaces
  ps_type="${ps_type%!}"
  ps_type="${ps_type// /}"
}

main() {
  #  ===============================================
  #  RESOLVE PROJECT DIRECTORY
  #  ===============================================
  # Priority: $1 argument, then PRJ_DIR env var, then current directory.
  local prj="${1:-${PRJ_DIR:-$PWD}}"
  [[ -d "${prj}" ]] || fatal "Project directory '${prj}' not found" 1
  cd "${prj}" || fatal "Unable to enter project directory '${prj}'" 1
  PRJ_DIR="$(pwd)"
  local version_file="${PRJ_DIR}/version.txt"
  local out_file="${PRJ_DIR}/a.md"
  info "Project directory '${PRJ_DIR}'"

  [[ -f "${version_file}" ]] || fatal "version.txt not found at '${version_file}'" 2

  #  ===============================================
  #  SNAPSHOT VERSION FROM version.txt
  #  ===============================================
  local snapshot_version
  snapshot_version="$(head -n 1 "${version_file}" | sed 's/^[#[:space:]]*//' | awk '{print $1}')"
  [[ -n "${snapshot_version}" ]] || fatal "Unable to read version from '${version_file}'" 3
  if [[ "${snapshot_version}" != *-SNAPSHOT ]]; then
    fatal "version.txt version '${snapshot_version}' is not a -SNAPSHOT version" 4
  fi
  local xyz="${snapshot_version%-SNAPSHOT}"
  info "Snapshot version '${snapshot_version}', release version 'v${xyz}'"

  #  ===============================================
  #  LAST GIT TAG
  #  ===============================================
  local raw_tag
  raw_tag="$(git -C "${PRJ_DIR}" describe --tags --abbrev=0 2>/dev/null)"
  [[ -n "${raw_tag}" ]] || fatal "Unable to find last git tag (git describe --tags --abbrev=0)" 5
  local tag_version="${raw_tag#v}"
  info "Last git tag '${raw_tag}' (version '${tag_version}')"

  if [[ "${tag_version}" == "${xyz}" ]]; then
    fatal "Last git tag '${raw_tag}' already matches version '${xyz}': release notes already prepared" 6
  fi

  #  ===============================================
  #  COLLECT TITLES SINCE LAST TAG (oldest -> newest)
  #  ===============================================
  task "Collecting commit titles since '${raw_tag}'"
  local -a type_order=()   # type group names, in first-appearance order
  local -a title_type=()   # parallel: type of each kept title
  local -a title_line=()   # parallel: formatted "- type(scope): title" line
  local subject k known

  while IFS= read -r subject; do
    [[ -z "${subject}" ]] && continue
    parse_subject "${subject}"
    [[ "${ps_has_colon}" -eq 1 ]] || continue
    [[ "${ps_type}" == "chore" ]] && continue
    [[ -z "${ps_type}" ]] && continue
    if [[ -n "${ps_scope}" ]]; then
      title_line+=("- ${ps_type}(${ps_scope}): ${ps_title}")
    else
      title_line+=("- ${ps_type}: ${ps_title}")
    fi
    title_type+=("${ps_type}")
    known=0
    for k in "${type_order[@]}"; do
      [[ "${k}" == "${ps_type}" ]] && known=1 && break
    done
    [[ ${known} -eq 0 ]] && type_order+=("${ps_type}")
  done < <(git -C "${PRJ_DIR}" log --reverse --format='%s' "${raw_tag}..HEAD")

  if [[ ${#title_line[@]} -eq 0 ]]; then
    warn "No conventional-commit titles found since '${raw_tag}' (chore commits excluded)"
  else
    info "Collected ${#title_line[@]} title(s) across ${#type_order[@]} type group(s)"
  fi

  #  ===============================================
  #  WRITE a.md
  #  ===============================================
  task "Writing release-preparation notes to '${out_file}'"
  {
    echo ""
    echo "# v${xyz} Release Preparation Notes"
    echo ""
    sed 's/\r$//' "${version_file}"
    echo ""
    echo "## v${xyz} changelog"
    echo ""

    local ty i
    for ty in "${type_order[@]}"; do
      echo "${ty}"
      echo ""
      for i in "${!title_type[@]}"; do
        [[ "${title_type[$i]}" == "${ty}" ]] && echo "${title_line[$i]}"
      done
      echo ""
    done

    echo "## v${xyz} commit list"
    echo ""
    echo "List of commit messages (type, scope, title and body, from oldest after last tag to newest HEAD)"
    echo ""

    local record body line
    while IFS= read -r -d '' record; do
      subject="${record%%$'\n'*}"
      if [[ "${record}" == *$'\n'* ]]; then
        body="${record#*$'\n'}"
      else
        body=""
      fi
      # strip CR and trailing blank lines from the body
      body="${body//$'\r'/}"
      body="${body%"${body##*[![:space:]]}"}"

      parse_subject "${subject}"
      if [[ "${ps_has_colon}" -eq 1 && -n "${ps_scope}" ]]; then
        echo "- ${ps_type}(${ps_scope}): ${ps_title}"
      elif [[ "${ps_has_colon}" -eq 1 ]]; then
        echo "- ${ps_type}: ${ps_title}"
      else
        echo "- ${subject}"
      fi
      if [[ -n "${body}" ]]; then
        while IFS= read -r line; do
          if [[ -n "${line}" ]]; then
            echo "  ${line}"
          else
            echo ""
          fi
        done <<< "${body}"
      fi
    done < <(git -C "${PRJ_DIR}" log --reverse -z --format='%s%n%b' "${raw_tag}..HEAD")
  } > "${out_file}"

  ok "Release-preparation notes written to '${out_file}'"
}

main "$@"
