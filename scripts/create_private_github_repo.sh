#!/usr/bin/env bash
set -euo pipefail
OWNER="${1:-sudopimp}"
REPO="${2:-robotrola}"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI 'gh' is required. Install it, then run: gh auth login"
  exit 1
fi

gh auth status >/dev/null

git init
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "https://github.com/${OWNER}/${REPO}.git"
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "Initial Robotrola Core SOTA 2026 hardware and software scaffold"
fi

gh repo create "${OWNER}/${REPO}" --private --source=. --remote=origin --push --description "Robotrola Core SOTA 2026 humanoid hardware, CAD, ROS 2, firmware, simulation, and safety R&D"

echo "Created private repo: https://github.com/${OWNER}/${REPO}"
