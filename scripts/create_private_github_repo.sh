#!/usr/bin/env bash
# Create/push sudopimp/robotrola. Aborts unless gh user is sudopimp.
set -euo pipefail
OWNER="${1:-sudopimp}"
REPO="${2:-robotrola}"
VIS="${3:-public}"   # public | private

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI 'gh' is required."
  exit 1
fi

USER="$(gh api user --jq .login)"
if [[ "$USER" != "sudopimp" ]]; then
  echo "ABORT: gh user is '$USER' (expected sudopimp). Refuse to push."
  exit 1
fi

echo "Authenticated as: $USER"
make diligence

if [[ ! -d .git ]]; then
  git init
  git branch -M main
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  if gh repo view "${OWNER}/${REPO}" >/dev/null 2>&1; then
    git remote add origin "https://github.com/${OWNER}/${REPO}.git"
  else
    gh repo create "${OWNER}/${REPO}" "--${VIS}" \
      --description "Robotrola Core — open research humanoid platform (42-DOF, safety, firmware, BOM, ROS 2)" \
      --source=. --remote=origin --push
    echo "Created https://github.com/${OWNER}/${REPO}"
    exit 0
  fi
fi

git push -u origin main
echo "Pushed https://github.com/${OWNER}/${REPO}"
