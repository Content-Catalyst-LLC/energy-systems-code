using DelimitedFiles

function main(root::String)
    input = joinpath(root, "outputs", "tables", "feeder_summary.csv")
    output = joinpath(root, "outputs", "tables", "julia_feeder_summary.csv")

    lines = readlines(input)
    open(output, "w") do io
        println(io, "feeder,utilization,headroom_mva,estimated_resistive_loss_kw")
        for line in lines[2:end]
            f = split(line, ',')
            println(io, "$(f[1]),$(f[5]),$(f[6]),$(f[8])")
        end
    end
    println("Wrote ", output)
end

main(length(ARGS) >= 1 ? ARGS[1] : ".")
