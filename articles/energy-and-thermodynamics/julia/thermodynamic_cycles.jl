using DelimitedFiles

function parse_rows(path::String)
    raw = readdlm(path, ',', Any, '\n')
    header = String.(raw[1, :])
    rows = Vector{Dict{String, Any}}()
    for i in 2:size(raw, 1)
        row = Dict{String, Any}()
        for j in eachindex(header)
            row[header[j]] = raw[i, j]
        end
        push!(rows, row)
    end
    return rows
end

function asfloat(value)
    return value isa Number ? Float64(value) : parse(Float64, String(value))
end

function main()
    article_dir = length(ARGS) >= 1 ? ARGS[1] : "."
    input_path = joinpath(article_dir, "data", "raw", "thermal_processes.csv")
    output_path = joinpath(article_dir, "outputs", "tables", "julia_cycle_metrics.csv")
    rows = parse_rows(input_path)

    open(output_path, "w") do io
        println(io, "scenario,carnot_efficiency,actual_efficiency,work_output_mj,heat_rejected_mj,entropy_generation_mj_per_k,first_law_residual_mj")
        for row in rows
            scenario = String(row["scenario"])
            hot = asfloat(row["hot_temperature_k"])
            cold = asfloat(row["cold_temperature_k"])
            heat_input = asfloat(row["heat_input_mj"])
            fraction = asfloat(row["second_law_fraction"])
            carnot = 1.0 - cold / hot
            actual = carnot * fraction
            work = heat_input * actual
            rejected = heat_input - work
            entropy_generation = rejected / cold - heat_input / hot
            residual = heat_input - work - rejected
            println(io, join((scenario, carnot, actual, work, rejected, entropy_generation, residual), ','))
        end
    end
    println("Wrote ", output_path)
end

main()
