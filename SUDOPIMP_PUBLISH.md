# Publish checklist (`sudopimp/robotrola`)

1. `gh api user --jq .login` prints `sudopimp`
2. `make diligence` exits 0
3. README badges / claims matrix still honest
4. `git push origin main`

```bash
cd robotrola-core   # or clone root
make diligence
git remote -v       # → github.com/sudopimp/robotrola
git push -u origin main
```
