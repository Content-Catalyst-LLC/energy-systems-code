struct ConversionStage
    name::String
    efficiency::Float64
    function ConversionStage(name, efficiency)
        0.0 <= efficiency <= 1.0 || error("efficiency must be in [0, 1]")
        new(name, efficiency)
    end
end
function run_chain(input, stages)
    current = input
    for stage in stages
        output = current * stage.efficiency
        println("$(stage.name),$(current),$(stage.efficiency),$(output),$(current-output)")
        current = output
    end
    return current
end
println("stage,input_kwh,efficiency,output_kwh,loss_kwh")
useful = run_chain(1000.0, [ConversionStage("distribution", .975), ConversionStage("inverter", .965),
    ConversionStage("motor", .925), ConversionStage("drive", .940)])
println(stderr, "overall_efficiency=$(useful/1000.0)")
