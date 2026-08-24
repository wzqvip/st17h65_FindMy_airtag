#!/usr/bin/env python3
import sys
import os
import argparse
from cryptography.hazmat.primitives.asymmetric import ec

def generate_st17h_keys_header(nkeys=50, interval_sec=3600, output_file="FindMy/source/keys_config.h"):
    print(f"Generating {nkeys} rolling keys for ST17H65 / ST17H66...")
    keys_bytes = []
    
    for i in range(nkeys):
        priv = ec.generate_private_key(ec.SECP224R1())
        pub = priv.public_key().public_numbers()
        x_bytes = pub.x.to_bytes(28, byteorder='big')
        keys_bytes.append(x_bytes)
        
    lines = []
    lines.append('#ifndef KEYS_CONFIG_H')
    lines.append('#define KEYS_CONFIG_H')
    lines.append('')
    lines.append('#include "bcomdef.h"')
    lines.append('')
    lines.append('/* Auto-generated Rolling Keys Configuration for ST17H65/ST17H66 */')
    lines.append(f'#define ROLLING_KEYS_COUNT {nkeys}')
    lines.append(f'#define SBP_ROTATE_KEY_PERIOD_MS {interval_sec * 1000}UL')
    lines.append('')
    lines.append(f'static const uint8 g_rolling_public_keys[{nkeys}][28] = {{')
    
    for idx, kb in enumerate(keys_bytes):
        hex_str = ", ".join([f"0x{b:02x}" for b in kb])
        comma = "," if idx < nkeys - 1 else ""
        lines.append(f'    {{{hex_str}}}{comma}')
        
    lines.append('};')
    lines.append('')
    lines.append('#endif /* KEYS_CONFIG_H */')
    lines.append('')
    
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        
    print(f"Successfully wrote {nkeys} rolling keys to {output_file}!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ST17H65/ST17H66 Rolling Keys Generator")
    parser.add_argument("-n", "--nkeys", type=int, default=50, help="Number of rolling keys (default: 50)")
    parser.add_argument("-t", "--interval", type=int, default=3600, help="Key rotation period in seconds (default: 3600 = 1 hour)")
    parser.add_argument("-o", "--output", type=str, default="FindMy/source/keys_config.h", help="Output header path")
    args = parser.parse_args()
    
    generate_st17h_keys_header(args.nkeys, args.interval, args.output)
