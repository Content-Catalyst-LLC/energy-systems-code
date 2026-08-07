using DelimitedFiles

function main(root::String)
    input = joinpath(root, "outputs", "tables", "resilience_scenarios.csv")
    output = joinpath(root, "outputs", "tables", "julia_resilience_summary.csv")

    lines = readlines(input)
    open(output, "w") do io
        println(io, "scenario,annualized_risk_million_usd,service_retained_fraction")
        for line in lines[2:end]
            f = split(line, ',')
            println(io, "$(f[1]),$(f[5]),$(f[4])")
        end
    end
    println("Wrote ", output)
end

main(length(ARGS) >= 1 ? ARGS[1] : ".")
