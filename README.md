# VFD Toolkit

A Python/Flask toolkit combining three practical VFD (Variable Frequency
Drive) engineering calculators: energy savings estimation, sizing/derating,
and a harmonics risk screening tool.

## Why this exists

VFD retrofit and selection decisions come up constantly in HVAC project
work — "how much will slowing this pump down actually save?", "will this
drive need derating at our site's altitude?", "is this VFD load going to
cause harmonic problems?" This toolkit answers all three with transparent,
documented calculations rather than black-box numbers.

## Tools included

### 1. Energy Savings Calculator (Affinity Laws)
Uses the pump/fan affinity laws (Power ∝ Speed³) to estimate energy savings
from VFD speed reduction. Critically, this tool also applies a **static
head correction** — real systems with a static head component (elevation
lift, fixed pressure requirement) see less savings than the pure cube law
predicts, since static head doesn't reduce with speed. Both the optimistic
pure cube-law figure and the more realistic corrected figure are shown
side by side.

### 2. Sizing & Selection Calculator
Applies typical temperature (~2%/°C above 40°C) and altitude (~1%/100m
above 1000m) derating guidelines to recommend a VFD rating for given site
conditions — clearly flagged as generic reference curves requiring
verification against the actual manufacturer's datasheet.

### 3. Harmonics / Power Quality Screening
A deliberately simple **screening heuristic** — VFD load as a percentage
of transformer/system capacity — used as a rough first-pass risk
indicator. This is explicitly NOT a substitute for a formal IEEE 519
harmonic study, which requires system short-circuit ratio, VFD switching
characteristics, and detailed load composition data this tool doesn't have.

## Tech stack

- **Backend:** Python 3, Flask
- **Frontend:** Server-rendered Jinja2 templates (tabbed navigation), vanilla CSS
- **No database, no external services** — pure calculation tool

## Getting started

```bash
git clone https://github.com/<your-username>/vfd-toolkit.git
cd vfd-toolkit
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5007** in your browser.

## Project structure

```
vfd-toolkit/
├── app.py              # Flask routes for all 3 tools
├── calculator.py         # Energy savings, sizing/derating, harmonics logic
├── requirements.txt
└── templates/
    ├── base.html           # Shared layout + tab navigation
    ├── energy.html         # Energy savings calculator
    ├── sizing.html         # Sizing & derating calculator
    └── harmonics.html      # Harmonics screening tool
```

## Roadmap / possible extensions

- Payback period calculation (savings vs. VFD purchase cost)
- Multiple VFD comparison (side-by-side speed reduction scenarios)
- Proper IEEE 519 Isc/IL-based screening (requires system impedance input)

## License

MIT — free to use and adapt.
