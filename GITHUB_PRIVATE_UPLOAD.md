
# Create private GitHub repository

The connected GitHub login detected in ChatGPT was `sudopimp`, but the available connector actions in this environment do not include repo creation or push. Use this from your local machine:

```bash
unzip robotrola_core_sota2026_repo.zip
cd robotrola_core_sota2026
bash scripts/create_private_github_repo.sh sudopimp robotrola
```

Manual alternative:

```bash
gh repo create sudopimp/robotrola --private --description "Robotrola Core SOTA 2026 humanoid hardware/software R&D"
git init
git add .
git commit -m "Initial Robotrola Core SOTA 2026 hardware and software scaffold"
git branch -M main
git remote add origin https://github.com/sudopimp/robotrola.git
git push -u origin main
```
