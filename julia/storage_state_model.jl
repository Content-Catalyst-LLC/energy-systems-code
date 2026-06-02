# Lightweight Julia storage state-of-charge teaching model

demand = [420.0, 405.0, 395.0, 390.0, 410.0, 455.0, 520.0, 590.0]
renewables = [165.0, 172.0, 168.0, 160.0, 155.0, 165.0, 215.0, 298.0]

capacity = 720.0
soc = 300.0
eff = 0.94
states = Float64[]

for i in eachindex(demand)
    net = renewables[i] - demand[i]
    if net >= 0
        soc = min(capacity, soc + net * eff)
    else
        soc = max(0.0, soc - abs(net) / eff)
    end
    push!(states, soc)
end

mkpath(joinpath(@__DIR__, "..", "outputs", "tables"))
output = joinpath(@__DIR__, "..", "outputs", "tables", "julia_storage_states.csv")
open(output, "w") do io
    println(io, "hour,state_of_charge_mwh")
    for (hour, value) in enumerate(states)
        println(io, "$(hour),$(round(value, digits=3))")
    end
end

println("Wrote $output")
