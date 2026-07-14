# Learning data path

## 1) JSON episode scaffold

`lerobot/robotrola_lerobot_adapter.py` — single JSON episode for diligence.
Actuation frames require `safety_state == ACTIVE`.

## 2) v3-layout export (always available)

`lerobot/v3_layout.py` writes a **local** directory inspired by LeRobotDataset v3:

```text
dataset/
  meta/info.json
  meta/episodes.jsonl
  data/chunk-000/file-000.jsonl
  data/chunk-000/file-000.parquet   # if pyarrow installed
```

## 3) Official package bridge (optional)

`lerobot/official_adapter.py` + `scripts/record_lerobot_episode.py`:

```bash
# default: v3-layout only (no torch)
python scripts/record_lerobot_episode.py -o /tmp/robotrola_ep
# → LEROBOT_PATH_OK  hub_upload=not_performed

# optional heavy stack
pip install -e ".[lerobot]"
python scripts/record_lerobot_episode.py -o /tmp/robotrola_ep
# writes meta/official_lerobot_bridge.json when package APIs are detected
```

Safety gate: `SafetyGatedRecorder.add_approved` refuses non-`ACTIVE` states.

### What is **not** claimed

- Automatic Hugging Face Hub upload
- Full video (MP4) encoding pipeline
- Bit-identical Hub dataset stats vs official teleop CLI

## 4) Hub push (operator only — requires your token)

Robotrola **never** uploads from library code. When you have a local dataset and
want Hub hosting:

```bash
# 1) Create HF account + token with write access
# 2) Login
huggingface-cli login

# 3) Prefer official lerobot dataset tools for your installed version, e.g.:
#    - convert / push helpers documented at
#      https://huggingface.co/docs/lerobot
#    - or upload the local folder as a dataset repo:
huggingface-cli upload your-user/robotrola-bench-demo /path/to/local/dataset --repo-type dataset

# 4) Never commit HF tokens to this repository
```

If `lerobot` package version APIs change, keep using the local **v3-layout**
export as the durable interchange format and re-bridge when ready.

## Lab next

- Camera streams as MP4 shards
- Full teleop record CLI matching HF tutorials
- CI job with `lerobot` only if torch cache budget allows
