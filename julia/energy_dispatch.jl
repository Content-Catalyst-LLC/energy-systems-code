# Dependency-light Julia energy dispatch example.

demand = [42, 40, 38, 36, 35, 39, 48, 55, 61, 64, 66, 67]
solar =  [0,  0,  0,  0,  2,  8, 18, 34, 48, 58, 62, 64]
wind =   [18, 16, 15, 14, 16, 24, 30, 26, 22, 20, 18, 16]

battery_capacity = 50.0
battery_state = 10.0
charge_efficiency = 0.92
discharge_efficiency = 0.92
unmet_total = 0.0
curtailed_total = 0.0

for hour in eachindex(demand)
    renewable = solar[hour] + wind[hour]
    net = renewable - demand[hour]
    global battery_state, unmet_total, curtailed_total

    if net >= 0
        available_space = battery_capacity - battery_state
        charged = min(net * charge_efficiency, available_space)
        battery_state += charged
        curtailed_total += max(0.0, net - charged / charge_efficiency)
    else
        deficit = abs(net)
        discharge_needed = deficit / discharge_efficiency
        discharged = min(discharge_needed, battery_state)
        battery_state -= discharged
        unmet_total += max(0.0, deficit - discharged * discharge_efficiency)
    end
end

println("Julia energy dispatch summary")
println("Final battery state: ", round(battery_state, digits=3), " MWh")
println("Unmet demand: ", round(unmet_total, digits=3), " MWh")
println("Curtailed renewable energy: ", round(curtailed_total, digits=3), " MWh")
