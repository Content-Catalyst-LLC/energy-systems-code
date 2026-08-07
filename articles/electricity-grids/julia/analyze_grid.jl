using DelimitedFiles

function main(root::String)
    input = joinpath(root, "outputs", "tables", "branch_flows.csv")
    output = joinpath(root, "outputs", "tables", "julia_branch_summary.csv")

    lines = readlines(input)
    open(output, "w") do io
        println(io, "branch,flow_mw,utilization")
        for line in lines[2:end]
            f = split(line, ',')
            println(io, "$(f[1]),$(f[4]),$(f[6])")
        end
    end
    println("Wrote ", output)
end

main(length(ARGS) >= 1 ? ARGS[1] : ".")
