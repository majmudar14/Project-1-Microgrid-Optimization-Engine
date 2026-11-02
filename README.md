# Microgrid Optimization Using Linear Programming

## Project Overview

This project develops a deterministic linear programming model to minimize the daily operating cost of a microgrid consisting of solar generation, battery energy storage, and electricity purchased from the grid.

The model is formulated in Python using PuLP and solved using the HiGHS optimization solver.

## Optimization Problem

**Objective:** Minimize total daily electricity procurement and solar variable operating costs over a 24-hour period.

**Decision variables:**
- Hourly grid electricity purchases
- Battery charging and discharging rates
- Battery stored energy
- Solar generation curtailment
- Initial battery state of charge

**Constraints:**
- Hourly electricity supply-demand balance
- Battery charging and discharging power limits
- Battery energy capacity
- Charging and discharging efficiency
- Intertemporal battery energy balance
- Cyclic initial and terminal battery energy

## Model Parameters

| Parameter | Value |
|---|---|
| Optimization horizon | 24 hours |
| Solar generation capacity | 30 MW |
| Battery storage capacity | 50 MWh |
| Battery power rating | 15 MW |
| Battery round-trip efficiency | 95% |
| Solar marginal operating cost | $5/MWh (illustrative) |
| Grid electricity prices | $25–$120/MWh (synthetic hourly data) |

## Results

For the current synthetic dataset, the model produces an optimal daily operating cost of approximately **$11,099.24**.

The optimizer selects a cyclic battery schedule with a starting and ending state of charge of approximately 0%. No solar curtailment is required under the tested conditions.

## Technologies

- Python
- pandas
- PuLP
- HiGHS

## Running the Model

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the program:

```bash
python app.py
```

## Limitations and Future Directions

This model assumes deterministic knowledge of electricity demand, solar availability, and electricity prices. It also excludes battery degradation, capital investment costs, and detailed electrical network constraints.

Potential future extensions include stochastic optimization, robust optimization, scenario-based uncertainty modeling, and comparisons with alternative operating strategies.

The project serves as an independent introduction to mathematical optimization and operations research applied to energy systems.