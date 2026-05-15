#!/usr/bin/env python3
"""Force-match LX3 platform on the comma device before FW versions exist."""
import os, sys
target = "/data/params/d/CarModelOverride"
if not os.path.isdir(os.path.dirname(target)):
    print(f"Run this on the comma device, not the codespace.")
    sys.exit(1)
with open(target, "w") as f:
    f.write("HYUNDAI_PALISADE_LX3_HEV")
print(f"Wrote HYUNDAI_PALISADE_LX3_HEV to {target}. Reboot the device.")
