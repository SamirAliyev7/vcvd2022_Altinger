# Magic Formula Tire Model — Vehicle Components & Vehicle Dynamics

**FH Oberösterreich · WS 2025**

---

## Author

| Field      | Value        |
|------------|--------------|
| Name       | Samir Aliyev |
| Student ID | 2510787008   |

---

## Description

Python implementation of the **Pacejka Magic Formula** tire model for pure-slip conditions.

Computes and plots:
- **Fx** — Brake (longitudinal) force over longitudinal slip κ (0–100 %)
- **Fy** — Side force at fixed slip angle α (pure-slip, constant over κ)

Multiple normal-force curves (Fz) are overlaid on each plot, matching the style of
Figures 19 & 20 in the reference paper.

**Reference:**
> Bakker, E., Nyborg, L., Pacejka, H.B. (1987).
> *Tyre Modelling for Use in Vehicle Dynamics Studies.*
> SAE Transactions.

---

## Repository Structure

```
.
├── p2510787008.py          # Main entry point (run this)
├── tire_model.py           # TireModel class — Magic Formula equations
├── plotter.py              # Plotter class — matplotlib output
├── coefficients_fy.json    # Fy coefficients (Table 2 & 3, Bakker 1987)
├── coefficients_fx.json    # Fx coefficients (Table 2, Bakker 1987)
├── plots/                  # Output directory for generated PNGs
└── README.md
```

---

## Dependencies

Install with conda (recommended):

```bash
conda create --name vcvd2025 scipy matplotlib numpy python
conda activate vcvd2025
```

Or with pip:

```bash
pip install scipy matplotlib numpy
```

---

## Usage

```bash
python p2510787008.py --slip <alpha_deg> --weight <vehicle_kg> --mu <friction>
```

### Arguments

| Argument   | Description                                | Default |
|------------|--------------------------------------------|---------|
| `--slip`   | Slip angle α in degrees                    | 2.0     |
| `--weight` | Vehicle mass in kg                         | 1500.0  |
| `--mu`     | Peak friction coefficient μ ∈ [0, 1]       | 1.0     |

### Sample calls

```bash
# Alpha = 2°, 1500 kg car, dry tarmac (mu=1.0)
python p2510787008.py --slip 2 --weight 1500 --mu 1.0

# Alpha = 5°, 1800 kg SUV, wet road (mu=0.8)
python p2510787008.py --slip 5 --weight 1800 --mu 0.8

# Alpha = 2°, 1500 kg car, icy road (mu=0.2)
python p2510787008.py --slip 2 --weight 1500 --mu 0.2
```

Plots are saved to the `plots/` directory as PNG files.

---

## Notes on Parameters

- **Fz per wheel** is derived from `weight × g / 4` (equal load distribution, `scipy.constants.g` used).
- **μ** scales the peak force D in the Magic Formula (D ∝ μ · Fz).
- Camber angle γ is set to **0** (not a required argument per assignment spec).
- Tabular coefficients are loaded from JSON files — no hardcoded magic numbers in Python source.

---

## Coding Guidelines Applied

- Google Python style (pylint `--rcfile ./code_guideline/googlePyLintSettings.cfg`)
- One class per file (`TireModel`, `Plotter`)
- No single-letter variable names
- Methods < 72 lines of code
- No global variables
- No hardcoded physical constants (`scipy.constants.g`)
- `argparse` for all CLI inputs
- Default values for all parameters
- JSON/CSV for tabular data
- Proper citation comments in source
