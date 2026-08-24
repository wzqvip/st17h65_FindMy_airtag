# ST17H65 / ST17H66 FindMy Firmware (Rolling Keys Support)

Firmware for Lenze ST17H66 / ST17H65 / PHY6202 chip that advertises to the Apple FindMy network, based on SDK v3.1.1.2. Enhanced with **native Rolling Keys (Key Rotation) support**.

---

## 🔑 Rolling Keys Setup

Generate a set of rotating public keys using `generate_keys_st17h.py`:

```bash
# Generate 50 rolling keys with 1-hour (3600s) rotation period
python generate_keys_st17h.py -n 50 -t 3600
```

This will automatically create/update `FindMy/source/keys_config.h` containing:
- `ROLLING_KEYS_COUNT`: Number of rotating keys (e.g. 50).
- `SBP_ROTATE_KEY_PERIOD_MS`: Rotation period in milliseconds (e.g. 3,600,000 ms).
- `g_rolling_public_keys`: Array of 28-byte public keys.

---

## 🛠️ Compile Firmware

### Compile with Keil uVision (Recommended)
1. Open `FindMy/FindMy.uvprojx` in Keil uVision.
2. Build the project. The output binary/hex will be generated in `FindMy/bin/`.

### Compile with GCC (Experimental)
```bash
git clone https://github.com/ARM-software/CMSIS_5
cd FindMy
make
```
