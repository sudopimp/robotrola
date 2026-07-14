# Learning data path

## 1) JSON episode scaffold (always available)

`lerobot/robotrola_lerobot_adapter.py` writes a single JSON episode for diligence
and bench logs. Actuation frames are refused unless `safety_state == ACTIVE`.

## 2) v3-layout export (Phase-0+)

`lerobot/v3_layout.py` writes a **local** directory inspired by LeRobotDataset v3:

```text
dataset/
  meta/info.json
  meta/episodes.jsonl
  data/chunk-000/file-000.jsonl
  data/chunk-000/file-000.parquet   # only if pyarrow installed
```

This is **not** Hugging Face Hub upload, MP4 video encoding, or the official
`lerobot` Python package training loop.

```bash
python - <<'PY'
from pathlib import Path
from robotrola.joint_filter import JointCommandFilter
from robotrola.msgs import JointCommandMsg
from lerobot.v3_layout import V3EpisodeBuilder

f = JointCommandFilter()
f.arm(); f.activate()
r = f.filter_command(JointCommandMsg("neck_yaw", 0.05, 0.05, 0.05))
assert r.ok
b = V3EpisodeBuilder("ep_demo")
b.add_frame({"joints": {"neck_yaw": 0.05}}, {"joint": "neck_yaw", "position_rad": 0.05}, r.mode)
print(b.export(Path("/tmp/robotrola_ep")))
PY
```

**Lab next:** official `lerobot` adapter, cameras as MP4, Hub push, teleop record CLI.
