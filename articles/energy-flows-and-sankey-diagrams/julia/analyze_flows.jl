using DelimitedFiles

function main(root::String)
    input = joinpath(root, "data", "processed", "energy_flows.csv")
    output = joinpath(root, "outputs", "tables", "julia_flow_summary.csv")

    lines = readlines(input)
    values = Float64[]
    for line in lines[2:end]
        fields = split(line, ',')
        push!(values, parse(Float64, fields[3]))
    end

    open(output, "w") do io
        println(io, "metric,value")
        println(io, "link_count,$(length(values))")
        println(io, "total_link_flow_mwh,$(sum(values))")
        println(io, "maximum_link_mwh,$(maximum(values))")
    end
    println("Wrote ", output)
end

main(length(ARGS) >= 1 ? ARGS[1] : ".")
