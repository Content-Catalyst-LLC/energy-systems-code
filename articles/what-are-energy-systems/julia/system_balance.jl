using DelimitedFiles

asfloat(value) = value isa Number ? Float64(value) : parse(Float64, strip(String(value)))

function main()
    root = normpath(joinpath(@__DIR__, ".."))
    input = joinpath(root, "data", "raw", "energy_links.csv")
    output = joinpath(root, "outputs", "tables", "julia_system_balance.csv")

    raw, header = readdlm(input, ',', Any, '\n'; header=true)
    columns = String.(vec(header))
    index = Dict(name => i for (i, name) in enumerate(columns))

    primary_input = 0.0
    output_energy = 0.0
    losses = 0.0
    unavailable = 0.0

    for row in eachrow(raw)
        input_mwh = asfloat(row[index["input_mwh"]])
        efficiency = asfloat(row[index["efficiency"]])
        availability = asfloat(row[index["availability"]])

        if input_mwh < 0.0
            error("input_mwh must be nonnegative")
        end
        if !(0.0 <= efficiency <= 1.0)
            error("efficiency must be within [0, 1]")
        end
        if !(0.0 <= availability <= 1.0)
            error("availability must be within [0, 1]")
        end

        available = input_mwh * availability
        primary_input += input_mwh
        output_energy += available * efficiency
        losses += available * (1.0 - efficiency)
        unavailable += input_mwh - available
    end

    residual = primary_input - output_energy - losses - unavailable
    tolerance = 1.0e-9 * max(1.0, abs(primary_input))
    abs(residual) <= tolerance || error("Energy-balance residual exceeds tolerance: $residual")

    mkpath(dirname(output))
    open(output, "w") do io
        println(io, "declared_link_input_mwh,link_output_mwh,link_losses_mwh,unavailable_mwh,balance_residual_mwh")
        println(io, "$(primary_input),$(output_energy),$(losses),$(unavailable),$(residual)")
    end

    println("Wrote $output")
    println("declared_link_input_mwh=$(primary_input)")
    println("balance_residual_mwh=$(residual)")
end

main()
