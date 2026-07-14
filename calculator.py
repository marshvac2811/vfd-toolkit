"""
calculator.py — VFD Toolkit: Energy Savings, Sizing/Derating, Harmonics Screening

Three independent calculation modules for VFD (Variable Frequency Drive)
applications, each documenting its own assumptions and limitations honestly
rather than overclaiming precision.
"""
import math

# ---------------------------------------------------------------------------
# 1. ENERGY SAVINGS (Affinity Laws)
# ---------------------------------------------------------------------------
# Pump/fan affinity laws (exact for a pure dynamic/no-static-head system):
#   Flow  ∝ Speed
#   Head  ∝ Speed²
#   Power ∝ Speed³
#
# Real systems with a static head component see LESS savings than the pure
# cube law predicts, because static head doesn't reduce with speed the way
# friction losses do. This tool applies a simple, commonly used correction:
# effective_power_ratio = static_fraction + (1 - static_fraction) * speed_ratio^3
# where static_fraction is the portion of total head that is static (0 =
# pure dynamic system, cube law applies exactly; higher = less savings).

def calculate_energy_savings(motor_kw: float, speed_reduction_pct: float,
                              static_head_fraction: float, annual_hours: float,
                              tariff_per_kwh: float) -> dict:
    if motor_kw <= 0:
        raise ValueError("Motor power must be greater than zero")
    if not (0 < speed_reduction_pct < 100):
        raise ValueError("Speed reduction percentage must be between 0 and 100")
    if not (0 <= static_head_fraction <= 100):
        raise ValueError("Static head fraction must be between 0 and 100")
    if annual_hours <= 0 or tariff_per_kwh <= 0:
        raise ValueError("Annual hours and tariff must be greater than zero")

    speed_ratio = 1 - (speed_reduction_pct / 100.0)
    static_frac = static_head_fraction / 100.0

    # Pure cube-law power ratio (no static head)
    pure_cube_power_ratio = speed_ratio ** 3

    # Corrected power ratio accounting for static head
    corrected_power_ratio = static_frac + (1 - static_frac) * (speed_ratio ** 3)

    original_power_kw = motor_kw
    reduced_power_kw_pure = motor_kw * pure_cube_power_ratio
    reduced_power_kw_corrected = motor_kw * corrected_power_ratio

    savings_kw_pure = original_power_kw - reduced_power_kw_pure
    savings_kw_corrected = original_power_kw - reduced_power_kw_corrected

    annual_savings_kwh_pure = savings_kw_pure * annual_hours
    annual_savings_kwh_corrected = savings_kw_corrected * annual_hours

    annual_savings_cost_pure = annual_savings_kwh_pure * tariff_per_kwh
    annual_savings_cost_corrected = annual_savings_kwh_corrected * tariff_per_kwh

    savings_pct_pure = (savings_kw_pure / original_power_kw) * 100
    savings_pct_corrected = (savings_kw_corrected / original_power_kw) * 100

    return {
        "motor_kw": motor_kw,
        "speed_reduction_pct": speed_reduction_pct,
        "speed_ratio": round(speed_ratio, 3),
        "static_head_fraction": static_head_fraction,
        "reduced_power_kw_pure": round(reduced_power_kw_pure, 2),
        "reduced_power_kw_corrected": round(reduced_power_kw_corrected, 2),
        "savings_pct_pure": round(savings_pct_pure, 1),
        "savings_pct_corrected": round(savings_pct_corrected, 1),
        "annual_hours": annual_hours,
        "tariff_per_kwh": tariff_per_kwh,
        "annual_savings_kwh_pure": round(annual_savings_kwh_pure, 0),
        "annual_savings_kwh_corrected": round(annual_savings_kwh_corrected, 0),
        "annual_savings_cost_pure": round(annual_savings_cost_pure, 0),
        "annual_savings_cost_corrected": round(annual_savings_cost_corrected, 0),
    }


# ---------------------------------------------------------------------------
# 2. SIZING & SELECTION (Temperature / Altitude Derating)
# ---------------------------------------------------------------------------
# Typical VFD manufacturer reference derating guidelines (varies by brand —
# this tool uses commonly cited generic figures and clearly flags them as
# reference-only, requiring verification against the actual selected VFD's
# datasheet):
#   - Rated ambient temperature: 40°C (standard rating point)
#   - Temperature derating: ~2% capacity reduction per °C above 40°C
#   - Rated altitude: 1000m (standard rating point)
#   - Altitude derating: ~1% capacity reduction per 100m above 1000m

STANDARD_VFD_SIZES_KW = [0.75, 1.1, 1.5, 2.2, 3.7, 5.5, 7.5, 11, 15, 18.5, 22,
                         30, 37, 45, 55, 75, 90, 110, 132, 160, 200, 250, 315]

RATED_AMBIENT_TEMP_C = 40
RATED_ALTITUDE_M = 1000
TEMP_DERATE_PCT_PER_C = 2.0
ALTITUDE_DERATE_PCT_PER_100M = 1.0


def calculate_sizing(motor_kw: float, ambient_temp_c: float, altitude_m: float) -> dict:
    if motor_kw <= 0:
        raise ValueError("Motor power must be greater than zero")
    if ambient_temp_c < -20 or ambient_temp_c > 70:
        raise ValueError("Ambient temperature must be between -20°C and 70°C")
    if altitude_m < 0 or altitude_m > 5000:
        raise ValueError("Altitude must be between 0 and 5000 m")

    temp_derate_pct = max(0, (ambient_temp_c - RATED_AMBIENT_TEMP_C)) * TEMP_DERATE_PCT_PER_C
    altitude_derate_pct = max(0, (altitude_m - RATED_ALTITUDE_M) / 100.0) * ALTITUDE_DERATE_PCT_PER_100M

    total_derate_pct = temp_derate_pct + altitude_derate_pct
    total_derate_pct = min(total_derate_pct, 60)  # cap — beyond this, special engineering needed regardless

    derating_factor = 1 - (total_derate_pct / 100.0)
    required_vfd_kw = motor_kw / derating_factor if derating_factor > 0 else motor_kw * 10

    recommended_vfd_kw = _round_up_to_standard_vfd(required_vfd_kw)

    return {
        "motor_kw": motor_kw,
        "ambient_temp_c": ambient_temp_c,
        "altitude_m": altitude_m,
        "temp_derate_pct": round(temp_derate_pct, 1),
        "altitude_derate_pct": round(altitude_derate_pct, 1),
        "total_derate_pct": round(total_derate_pct, 1),
        "derating_factor": round(derating_factor, 3),
        "required_vfd_kw": round(required_vfd_kw, 2),
        "recommended_vfd_kw": recommended_vfd_kw,
    }


def _round_up_to_standard_vfd(kw: float) -> float:
    for size in STANDARD_VFD_SIZES_KW:
        if size >= kw:
            return size
    return STANDARD_VFD_SIZES_KW[-1]


# ---------------------------------------------------------------------------
# 3. HARMONICS / POWER QUALITY SCREENING
# ---------------------------------------------------------------------------
# This is a SCREENING HEURISTIC only — VFD load as a percentage of total
# transformer/system capacity, used as a rough first-pass risk indicator.
# It is NOT a substitute for a proper IEEE 519 harmonic study, which
# requires actual system short-circuit capacity (Isc/IL ratio), VFD
# switching characteristics, and detailed load composition.

def screen_harmonics_risk(total_vfd_kva: float, transformer_kva: float) -> dict:
    if total_vfd_kva <= 0:
        raise ValueError("Total VFD load must be greater than zero")
    if transformer_kva <= 0:
        raise ValueError("Transformer capacity must be greater than zero")

    loading_pct = (total_vfd_kva / transformer_kva) * 100

    if loading_pct < 20:
        risk_level = "Low"
        guidance = "VFD load is a small fraction of transformer capacity — harmonic distortion is typically manageable without additional filtering, but this is not a guarantee."
    elif loading_pct < 40:
        risk_level = "Moderate"
        guidance = "VFD load is a meaningful fraction of transformer capacity — consider a harmonic filter or line reactor, and recommend a proper IEEE 519 study before finalizing."
    else:
        risk_level = "High"
        guidance = "VFD load is a large fraction of transformer capacity — harmonic filtering (active filter or multi-pulse drive) is likely needed. A formal IEEE 519 harmonic study is strongly recommended."

    return {
        "total_vfd_kva": total_vfd_kva,
        "transformer_kva": transformer_kva,
        "loading_pct": round(loading_pct, 1),
        "risk_level": risk_level,
        "guidance": guidance,
    }
