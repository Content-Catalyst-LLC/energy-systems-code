function main(root::String)
    input = joinpath(root,"outputs","tables","scenario_summary.csv")
    output = joinpath(root,"outputs","tables","julia_scenario_summary.csv")
    lines = readlines(input)
    open(output,"w") do io
        println(io,"scenario,final_capacity_gw")
        for line in lines[2:end]
            f = split(line, ',')
            println(io,"$(f[1]),$(f[3])")
        end
    end
end
main(length(ARGS)>=1 ? ARGS[1] : ".")
