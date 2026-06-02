fn main() {
    let actual_generation_mwh = 8200.0;
    let nameplate_mw = 300.0;
    let hours = 24.0;
    let capacity_factor = actual_generation_mwh / (nameplate_mw * hours);

    println!("actual_generation_mwh,nameplate_mw,hours,capacity_factor");
    println!("{},{},{},{}", actual_generation_mwh, nameplate_mw, hours, capacity_factor);
}
