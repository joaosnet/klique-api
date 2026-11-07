# Android & Mobile Pipeline

> 8 nodes · cohesion 0.29

## Key Concepts

- **subprocess** (9 connections)
- **display_and_optionally_install_apk()** (6 connections) — `scripts/build_android.py`
- **run()** (6 connections) — `scripts/hot_reload_android.py`
- **get_adb_device()** (4 connections) — `scripts/build_android.py`
- **Return the id of the first attached adb device, or None if none.** (1 connections) — `scripts/build_android.py`
- **CompletedProcess** (1 connections)
- **Path** (1 connections)
- **Execute a command showing live output.** (1 connections) — `scripts/hot_reload_android.py`

## Relationships

- [Setup Cookies Module](Setup_Cookies_Module.md) (1 shared connections)
- [Android & Mobile Pipeline](Android_&_Mobile_Pipeline.md) (1 shared connections)

## Source Files

- `scripts/build_android.py`
- `scripts/hot_reload_android.py`

## Audit Trail

- EXTRACTED: 10 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*