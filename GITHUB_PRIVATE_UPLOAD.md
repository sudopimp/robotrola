# Publishing this repository

Canonical remote:

```text
https://github.com/sudopimp/robotrola
```

## Create (if empty)

```bash
# must be authenticated as sudopimp
gh api user --jq .login   # → sudopimp

gh repo create sudopimp/robotrola --public \
  --description "Robotrola Core — open research humanoid: 42-DOF, safety, firmware, BOM, ROS 2" \
  --source=. --remote=origin --push
```

## Update

```bash
git add -A
git status
git commit -m "Describe change"
git push origin main
make diligence   # before push preferred
```

Do **not** push using the `waitdeadai` (or any other) GitHub account for this project.
