"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

# Two rules to kill SnG gas-brake feel without ever delaying a real brake:
# 1) Sign-flip dead band: tiny accel that flips sign held at coast.
# 2) Post-gas mild-brake suppression in SnG — ONLY when the lead is not
#    actually decelerating. If lead aLeadK indicates a real brake, the
#    mild-brake command passes through immediately.

DEAD_BAND               = 0.20  # m/s^2, half-width of the hold-at-coast region

GAS_PEAK_THRESH         = 0.30   # m/s^2 — sustained accel above this counts as gas
GAS_PEAK_DECAY_FRAMES   = 200    # 2s @ 100Hz of brake suppression after gas peak
SOFT_BRAKE_THRESH       = 0.50   # m/s^2 — only mild brakes below this are candidates
SNG_V_EGO_THRESH        = 5.0    # m/s — SnG regime threshold
LEAD_BRAKE_THRESH       = -0.20  # m/s^2 — below this, lead is genuinely braking


class GasBrakeHysteresis:
  def __init__(self):
    self.prev: float = 0.0
    self.gas_recent: int = 0

  def update(self, accel: float, v_ego: float = 10.0,
             lead_status: bool = False, lead_a: float = 0.0) -> float:
    if accel > GAS_PEAK_THRESH:
      self.gas_recent = GAS_PEAK_DECAY_FRAMES
    else:
      self.gas_recent = max(0, self.gas_recent - 1)

    # Spurious mild brake after gas peak (coast-down feel, not real lead brake).
    # Gated on lead NOT actually decelerating — if lead is braking, pass through.
    lead_not_braking = (not lead_status) or (lead_a >= LEAD_BRAKE_THRESH)
    if (v_ego < SNG_V_EGO_THRESH and self.gas_recent > 0 and lead_not_braking
        and -SOFT_BRAKE_THRESH < accel < 0):
      self.prev = 0.0
      return 0.0

    # Sign-flip dead band
    if abs(accel) <= DEAD_BAND and self.prev * accel < 0.0:
      self.prev = 0.0
      return 0.0

    self.prev = accel
    return accel
