from pathlib import Path
import os, shutil, csv, json, textwrap, zipfile, math, yaml, hashlib, subprocess, sys
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/mnt/data/robotrola_core_sota2026')
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)

def w(path, content, mode='w'):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, mode, encoding=None if 'b' in mode else 'utf-8') as f:
        f.write(content)
    return p

def copy_if(src, dst):
    s=Path(src)
    if s.exists():
        p=ROOT/dst
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s,p)
        return p

# ------------------------ Branding / assets ------------------------
for src, dst in [
    ('/mnt/data/robotrola-r01-eva-hero.png','assets/visual/robotrola-r01-eva-hero.png'),
    ('/mnt/data/robotrola-r01-eva-portrait.png','assets/visual/robotrola-r01-eva-portrait.png'),
    ('/mnt/data/esquema_técnico_del_robotrola_r_01_eva.png','assets/visual/robotrola-blueprint-r01-eva.png'),
    ('/mnt/data/página_web_de_robótica_open_source.png','assets/visual/repo_reference_home.png'),
    ('/mnt/data/arquitectura_y_diseño_de_robótica_robotrola.png','assets/visual/repo_reference_architecture.png'),
    ('/mnt/data/página_web_de_robotrola_seguridad_y_ética.png','assets/visual/repo_reference_safety.png'),
    ('/mnt/data/robótica_avanzada_con_diseño_elegante.png','assets/visual/og-clean.png'),
]: copy_if(src,dst)

# create logo svg
w('assets/brand/robotrola_mark.svg', '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-label="Robotrola mark">
  <rect width="512" height="512" rx="48" fill="#f5ead8"/>
  <circle cx="256" cy="256" r="182" fill="none" stroke="#8a4f21" stroke-width="8"/>
  <circle cx="256" cy="140" r="28" fill="none" stroke="#8a4f21" stroke-width="8"/>
  <path d="M256 168 L256 330 M156 214 L356 214 M186 368 L256 210 L326 368 M198 250 L146 326 M314 250 L366 326" fill="none" stroke="#8a4f21" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M92 256 C160 62 352 62 420 256 C352 450 160 450 92 256Z" fill="none" stroke="#b8793c" stroke-width="3" opacity=".65"/>
</svg>''')


print('Reference STL generation is embedded in the repository build script. Use /tools source as template.')
