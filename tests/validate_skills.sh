#!/usr/bin/env bash
# Validate every skill against the Agent Skills specification.
# Runs the reference validator when uvx is available, and always runs the built-in
# checks, so the test works without network access.
set -euo pipefail

REPO_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SKILLS_DIR="$REPO_DIR/skills"
status=0

fail() {
    echo "FAIL: $*" >&2
    status=1
}

for skill in "$SKILLS_DIR"/*/; do
    skill="${skill%/}"
    dir_name=$(basename "$skill")
    file="$skill/SKILL.md"
    [ -f "$file" ] || { fail "$dir_name has no SKILL.md"; continue; }

    if [ "$(head -1 "$file")" != "---" ]; then
        fail "$dir_name: SKILL.md does not start with frontmatter"
    fi
    name=$(awk '/^name:/{print $2; exit}' "$file")
    [ "$name" = "$dir_name" ] || fail "$dir_name: name '$name' does not match the directory"
    description=$(awk '/^description:/{sub(/^description:[[:space:]]*/,""); print; exit}' "$file")
    [ -n "$description" ] || fail "$dir_name: description is empty"
    [ "${#description}" -le 1024 ] || fail "$dir_name: description is longer than 1024 characters"

    keys=$(awk 'BEGIN{fm=0} /^---[[:space:]]*$/{fm++; next} fm==1 && /^[a-z-]+:/{sub(/:.*/,""); print}' "$file")
    for key in $keys; do
        case "$key" in
            name|description|license|compatibility|metadata|allowed-tools) ;;
            *) fail "$dir_name: frontmatter key '$key' is not in the Agent Skills specification" ;;
        esac
    done

    lines=$(wc -l < "$file")
    [ "$lines" -le 500 ] || fail "$dir_name: SKILL.md has $lines lines; the limit is 500"

    # shellcheck disable=SC2016
    while IFS= read -r ref; do
        target="$skill/$ref"
        [ -e "$target" ] || fail "$dir_name: references '$ref', which does not exist"
    done < <(grep -o '`\(\.\./[a-z-]*/\)\?\(references\|assets\)/[A-Za-z0-9_./-]*`' "$file" | tr -d '`' | sort -u)

    echo "ok: $dir_name"
done

if command -v uvx >/dev/null 2>&1; then
    for skill in "$SKILLS_DIR"/*/; do
        if ! uvx --from skills-ref agentskills validate "${skill%/}"; then
            fail "reference validator rejected $(basename "$skill")"
        fi
    done
else
    echo "note: uvx is not installed; the reference validator did not run"
fi

exit "$status"
