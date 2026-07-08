
# Robotrola Core — I+D Humanoide de Compañía Adulta SOTA 2026

**Repositorio privado sugerido:** `sudopimp/robotrola`  
**Estado:** base de fabricación e investigación; no es un producto certificado.  
**Alcance:** hardware, impresión 3D, electrónica, firmware, ROS 2, simulación, seguridad, calibración, validación y documentación de fabricación.  
**Sitio web:** excluido a propósito; la landing va en otro proyecto.

Robotrola Core es un repo privado, serio y safety-first para convertir Robotrola en un prototipo humanoide reproducible de laboratorio. Incluye geometría imprimible, BOM, cableado, software, simulación, firmware y documentación para avanzar desde concepto hacia prototipo real.

> No usar para contacto humano sin revisión mecánica, eléctrica, legal, de privacidad y de seguridad robótica.

## Incluye

- Piezas 3D de referencia en `cad/stl/` y fuentes paramétricas en `cad/scad/`.
- Descripción URDF/Xacro para RViz, Gazebo e integración ROS.
- BOM con componentes SOTA 2026: cómputo, sensores, actuadores, energía, seguridad, piel, docking y módulos de servicio.
- Workspace ROS 2: descripción, bringup, safety, percepción, control, teleoperación y mensajes.
- Librería Python para configuración, límites, feature flags, BOM, cinemática y validación.
- Firmware base para placa de seguridad ESP32-S3 con micro-ROS y bridge STM32/CAN/DYNAMIXEL.
- Plan de simulación con Gazebo + Isaac Sim / Isaac Lab.
- Adapter LeRobot y esquema de dataset para captura reproducible.
- Documentos de riesgo, privacidad, uso adulto, validación y manufactura.

## Subir como repo privado

```bash
bash scripts/create_private_github_repo.sh sudopimp robotrola
```

La herramienta GitHub conectada en este chat identifica tu login como `sudopimp`, pero no expone acciones de creación/push de repos privados. Por eso dejé el proyecto completo y un helper para subirlo desde tu máquina autenticada.
