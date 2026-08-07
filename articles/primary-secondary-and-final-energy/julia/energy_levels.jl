using DelimitedFiles

function main()
    root = dirname(dirname(@__FILE__))
    input_path = joinpath(root, "data", "raw", "energy_pathways.csv")
    output_path = joinpath(root, "outputs", "tables", "julia_energy_levels.csv")
    data, header = readdlm(input_path, ',', header=true)
    names = vec(header)
    idx(name) = findfirst(==(name), names)

    rows = String["pathway,primary_energy_mwh,secondary_energy_mwh,final_energy_mwh,useful_energy_mwh,service_energy_equivalent_mwh,residual_mwh"]
    for i in axes(data, 1)
        pathway = string(data[i, idx("pathway")])
        primary = parse(Float64, string(data[i, idx("primary_energy_mwh")]))
        conversion = parse(Float64, string(data[i, idx("conversion_efficiency")]))
        delivery = parse(Float64, string(data[i, idx("delivery_efficiency")]))
        end_use = parse(Float64, string(data[i, idx("end_use_efficiency")]))
        service_factor = parse(Float64, string(data[i, idx("service_factor")]))
        own_use = parse(Float64, string(data[i, idx("energy_sector_own_use_fraction")]))
        non_energy = parse(Float64, string(data[i, idx("non_energy_use_fraction")]))
        transformation_input = primary * (1 - own_use - non_energy)
        secondary = transformation_input * conversion
        final = secondary * delivery
        useful = final * end_use
        service = useful * service_factor
        losses = primary * own_use + primary * non_energy + (transformation_input-secondary) + (secondary-final) + (final-useful) + (useful-service)
        residual = primary - losses - service
        push!(rows, join([pathway, primary, secondary, final, useful, service, residual], ','))
    end
    open(output_path, "w") do io
        write(io, join(rows, "\n") * "\n")
    end
    println("Wrote ", output_path)
end

main()
