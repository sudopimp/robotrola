# Publicar core en GitHub (`sudopimp`)

```bash
cd "$(dirname "$0")"
git status
gh auth status   # asegurate de estar logueado como sudopimp, NO waitdeadai
gh repo create sudopimp/robotrola --public \
  --description "Robotrola Core SOTA 2026 — humanoid open R&D (ROS2, CAD, safety)" \
  --source=. --remote=origin --push
```

Si el repo ya existe vacío:

```bash
git remote add origin https://github.com/sudopimp/robotrola.git
git push -u origin main
```
