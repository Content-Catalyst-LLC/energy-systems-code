using DelimitedFiles

function main(root::String)
    input = joinpath(root, "data", "raw", "interval_demand.csv")
    output = joinpath(root, "outputs", "tables", "julia_interval_summary.csv")

    lines = readlines(input)
    values = Float64[]
    for line in lines[2:end]
        f = split(line, ',')
        push!(values, parse(Float64, f[2]))
    end

    open(output, "w") do io
        println(io, "metric,value")
        println(io, "peak_mw,$(maximum(values))")
        println(io, "average_mw,$(sum(values)/length(values))")
    end
    println("Wrote ", output)
end

main(length(ARGS) >= 1 ? ARGS[1] : ".")
