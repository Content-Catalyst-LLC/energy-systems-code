fn main() {
    let demand = [42.0, 40.0, 38.0, 36.0, 35.0, 39.0, 48.0, 55.0, 61.0, 64.0, 66.0, 67.0];
    let solar =  [0.0, 0.0, 0.0, 0.0, 2.0, 8.0, 18.0, 34.0, 48.0, 58.0, 62.0, 64.0];
    let wind =   [18.0, 16.0, 15.0, 14.0, 16.0, 24.0, 30.0, 26.0, 22.0, 20.0, 18.0, 16.0];

    let total_demand: f64 = demand.iter().sum();
    let total_renewable: f64 = solar.iter().zip(wind.iter()).map(|(s, w)| s + w).sum();

    println!("Rust energy balance summary");
    println!("Total demand: {:.2} MWh", total_demand);
    println!("Total renewable generation: {:.2} MWh", total_renewable);
    println!("Renewable share proxy: {:.3}", total_renewable / total_demand);
}
