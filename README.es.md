# Robotrola Core

**Plataforma abierta de investigación** para un humanoide de compañía adulta, safety-first y **no explícito**.

[English README](README.md) · [Sitio](https://robotrola.com) · [X @sudopimp](https://x.com/sudopimp) · [TikTok @robotrola](https://www.tiktok.com/@robotrola) · [Claims](docs/CLAIMS_MATRIX.md)

## Qué es / qué no es

| Sí | No |
|---|---|
| Paquete completo de lab: 42 DOF, CAD, BOM, safety, firmware, ROS, datos | Producto de consumo certificado |
| Demo re-ejecutable sin robot (`make diligence`) | Policy de biped lista en hardware |
| Camino bench → torso → cuerpo completo | SKU de fábrica |

## Demo en 90 segundos

```bash
git clone https://github.com/sudopimp/robotrola.git
cd robotrola
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make diligence
# → INVESTOR_DEMO_OK · dof=42
```

## Seguridad

Módulos de alto riesgo **apagados por defecto** (`configs/feature_flags.yaml`).  
Leé `SAFETY.md` y `DISCLAIMER.md` antes de cualquier prueba con personas.

## Licencias

- Software: Apache-2.0 (`LICENSE_SOFTWARE`)
- Hardware/CAD: CERN-OHL-S-2.0 (`LICENSE_HARDWARE`)
