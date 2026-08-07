using DelimitedFiles

function main(root::String)
    input = joinpath(root, "data", "processed", "eroi_projects.csv")
    output = joinpath(root, "outputs", "tables", "julia_eroi_summary.csv")

    lines = readlines(input)
    open(output, "w") do io
        println(io, "name,gross_output_mwh,invested_mwh,eroi")
        for line in lines[2:end]
            f = split(line, ',')
            name = f[1]
            gross = parse(Float64, f[2])
            invested = sum(parse.(Float64, f[3:10]))
            println(io, "$(name),$(gross),$(invested),$(gross / invested)")
        end
    end
    println("Wrote ", output)
end

main(length(ARGS) >= 1 ? ARGS[1] : ".")
