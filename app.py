import pandas as pd
import pulp

# Inputting data to initialize external data and provide context for power grids

# providing a set of hours in a day
hours = list(range(24))

# providing a maximum solar capacity to show the maximum potential solar generation in Megawatts:
max_solar_capacity = 30.0  # in MW

# providing a set of the rate of electricity consumption demanded in Megawatts:
demand_mw = [12, 11, 10, 10, 11, 13, 16, 20, 22, 21, 19, 18, 18, 19, 21, 23, 25, 26, 24, 21, 18, 16, 14, 12]

# providing a set of solar capacity factors to show availability of solar generation at each hour
solar_cf = [0, 0, 0, 0, 0, 0.05, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0, 0.95, 0.85, 0.7, 0.5, 0.25, 0.05, 0, 0, 0, 0, 0, 0]

# providing a set of grid prices at each hour
grid_price = [30, 25, 25, 28, 35, 45, 60, 85, 90, 75, 65, 60, 55, 60, 70, 95, 110, 120, 100, 80, 60, 50, 40, 35]

# providing the hourly price of solar power
solar_cost = 5.0  # $/MWh

# Combining above data vectors into a Pandas DataFrame container
df = pd.DataFrame({
    'hour': hours,
    'demand_mw': demand_mw,
    'solar_cf': solar_cf,
    'grid_price': grid_price
})
print(df)

# Formally defining the optimization problem in pulp
prob = pulp.LpProblem("Microgrid_Optimization", pulp.LpMinimize)

# Defining the parameters of the microgrid battery
battery_capacity = 50.0  # Maximum energy capacity in MWh
battery_efficiency = 0.95  # assuming 95% round trip efficiency factor
battery_initial_charge = prob.add_variable(
    "Initial_Battery_Energy",
    lowBound=0,
    upBound=battery_capacity
)
power_rating_max = 15.0 # The maximum rate at which we can charge/discharge the battery in MW in a given hour

# Defining a variable for each hour t (0 to 23) for future calculations
hours = range(24)

# Creating variables to establish the charge rate, discharge rate, energy level of the battery, grid power, and solar curtailment if necessary for each hour
battery_charge_rate = {t: prob.add_variable(f"Charge_Rate_{t}", lowBound=0, upBound=power_rating_max) for t in hours}
battery_discharge_rate = {t: prob.add_variable(f"Discharge_Rate_{t}", lowBound=0, upBound=power_rating_max) for t in hours}
battery_energy_level = {t: prob.add_variable(f"Energy_Level_{t}", lowBound=0, upBound=battery_capacity) for t in hours}
grid_power = {t: prob.add_variable(f"Grid_Power_{t}", lowBound=0) for t in hours}
solar_curtailment = {t: prob.add_variable(f"Solar_Curtailment_{t}", lowBound=0, upBound=solar_cf[t] * max_solar_capacity) for t in hours}

# Syncing the battery charge/discharge rate to its relationship with the energy level of the battery over time
# Assuming 95% round-trip efficiency, split equally between charging and discharging
charge_efficiency = battery_efficiency ** 0.5
discharge_efficiency = battery_efficiency ** 0.5

for t in hours:
    # The battery starts hour 0 at its initial charge.
    # In later hours, it starts at the previous hour's energy level.
    previous_energy = (
        battery_initial_charge
        if t == 0
        else battery_energy_level[t - 1]
    )

    # Link stored energy to charging and discharging
    prob += (
        battery_energy_level[t]
        == previous_energy
        + charge_efficiency * battery_charge_rate[t]
        - battery_discharge_rate[t] / discharge_efficiency
    ), f"Battery_Energy_Balance_{t}"


# Establishing power balance constraint ensuring power demand and charging rate match available supply
for t in hours:
    prob += (
        demand_mw[t] + battery_charge_rate[t] + solar_curtailment[t]
        == (solar_cf[t] * max_solar_capacity) + grid_power[t] + battery_discharge_rate[t]
    )

# Ensuring that the battery energy level returns to 50% of battery capacity at the end of each 24-hour period
prob += (
    battery_energy_level[23] - battery_initial_charge == 0
), "Terminal_Battery_Energy"

# Setting up the objective function to minimize the total cost of electricity purchased from the grid over the 24-hour period
prob += pulp.lpSum([
    grid_price[t] * grid_power[t]
    + solar_cost * (
        solar_cf[t] * max_solar_capacity
        - solar_curtailment[t]
    )
    for t in hours
])

# Solving the optimization problem and extracting the results, then informing the user of the status of the optimization problem
stats = prob.solve(pulp.HiGHS(msg=True))
print("Status:", stats.status_str)
print("Objective Value:", stats.objective)

# Informing the user of the optimal starting battery energy and optimal battery state of charge (SOC)
optimal_initial_energy = pulp.value(battery_initial_charge)
print(f"Optimal Starting Energy: {optimal_initial_energy:.2f} MWh")
print(f"Optimal Starting SOC: {100 * optimal_initial_energy / battery_capacity:.2f}%")

# Saving the results to a DataFrame for easier visualization
df['battery_charge_rate'] = [pulp.value(battery_charge_rate[t]) for t in hours]
df['battery_discharge_rate'] = [pulp.value(battery_discharge_rate[t]) for t in hours]
df['battery_energy_level'] = [battery_energy_level[t].varValue for t in hours]
df['grid_power'] = [grid_power[t].varValue for t in hours]
df['solar_curtailment'] = [pulp.value(solar_curtailment[t]) for t in hours]
print("\nOptimization Results Summary:")
print(df[['hour', 'demand_mw', 'grid_power', 'solar_curtailment', 'battery_energy_level', 'battery_charge_rate', 'battery_discharge_rate']])
