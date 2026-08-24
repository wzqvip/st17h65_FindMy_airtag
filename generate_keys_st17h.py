#!/usr/bin/env python3
import sys
import os
import argparse
import base64
import json
import random
from cryptography.hazmat.primitives.asymmetric import ec

def generate_st17h_keys(mode="rolling", nkeys=50, interval_sec=3600, prefix="ST17H", output_dir="output"):
    if mode == "single":
        nkeys = 1
        print("[Mode] SINGLE KEY (Traditional Single Static Key Mode)")
    else:
        if nkeys < 2:
            nkeys = 50
        print(f"[Mode] ROLLING KEYS ({nkeys} Rotating Keys, Interval: {interval_sec}s)")

    print(f"Generating {nkeys} keypairs...")
    
    pub_bytes_list = []
    priv_b64_list = []

    for i in range(nkeys):
        priv = ec.generate_private_key(ec.SECP224R1())
        priv_num = priv.private_numbers().private_value
        priv_bytes = priv_num.to_bytes(28, byteorder='big')
        priv_b64 = base64.b64encode(priv_bytes).decode('ascii')
        priv_b64_list.append(priv_b64)

        pub = priv.public_key().public_numbers()
        x_bytes = pub.x.to_bytes(28, byteorder='big')
        pub_bytes_list.append(x_bytes)

    # 1. Generate keys_config.h for ST17H65 / ST17H66 firmware compilation
    header_path = "FindMy/source/keys_config.h"
    lines = []
    lines.append('#ifndef KEYS_CONFIG_H')
    lines.append('#define KEYS_CONFIG_H')
    lines.append('')
    lines.append('#include "bcomdef.h"')
    lines.append('')
    lines.append(f'/* Auto-generated ST17H Config | Mode: {mode.upper()} | Count: {nkeys} */')
    lines.append(f'#define ROLLING_KEYS_COUNT {nkeys}')
    lines.append(f'#define SBP_ROTATE_KEY_PERIOD_MS {interval_sec * 1000}UL')
    lines.append('')
    lines.append(f'static const uint8 g_rolling_public_keys[{nkeys}][28] = {{')
    
    for idx, kb in enumerate(pub_bytes_list):
        hex_str = ", ".join([f"0x{b:02x}" for b in kb])
        comma = "," if idx < nkeys - 1 else ""
        lines.append(f'    {{{hex_str}}}{comma}')
        
    lines.append('};')
    lines.append('')
    lines.append('#endif /* KEYS_CONFIG_H */')
    lines.append('')
    
    os.makedirs(os.path.dirname(os.path.abspath(header_path)), exist_ok=True)
    with open(header_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  [+] Firmware Header: {header_path}")

    # 2. Generate devices.json for Macless-Haystack App/Web import
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, f"{prefix}_devices.json")
    
    tag_id = random.randint(1000000, 9999999)
    device_obj = {
        "id": tag_id,
        "colorComponents": [0, 1, 0, 1],
        "name": prefix,
        "privateKey": priv_b64_list[0],
        "icon": "",
        "isActive": True,
        "additionalKeys": priv_b64_list[1:] if nkeys > 1 else []
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump([device_obj], f, indent=2)
    print(f"  [+] App Import File: {json_path}")
    print("\nGeneration Complete! Ready for Keil / GCC Firmware Compilation & App Import.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ST17H65/ST17H66 Key Generator (Single Key & Rolling Keys Modes)")
    parser.add_argument("-m", "--mode", type=str, choices=["single", "rolling"], default="rolling", help="Key mode: 'single' (1 static key) or 'rolling' (multi-key rotation)")
    parser.add_argument("-n", "--nkeys", type=int, default=50, help="Number of keys for rolling mode (default: 50)")
    parser.add_argument("-t", "--interval", type=int, default=3600, help="Key rotation period in seconds (default: 3600 = 1 hour)")
    parser.add_argument("-p", "--prefix", type=str, default="ST17H", help="Tag name prefix (default: ST17H)")
    parser.add_argument("-o", "--output-dir", type=str, default="output", help="Output directory for devices.json")
    args = parser.parse_args()
    
    generate_st17h_keys(args.mode, args.nkeys, args.interval, args.prefix, args.output_dir)
