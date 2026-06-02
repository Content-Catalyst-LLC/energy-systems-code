model BatteryStorageTeachingModel
  parameter Real capacity = 720 "Energy capacity MWh";
  parameter Real initialSOC = 300 "Initial state of charge MWh";
  parameter Real chargeEfficiency = 0.94;
  parameter Real dischargeEfficiency = 0.94;
  Real soc(start=initialSOC) "State of charge MWh";
  input Real chargePower "Charge power MW";
  input Real dischargePower "Discharge power MW";
equation
  der(soc) = chargePower * chargeEfficiency - dischargePower / dischargeEfficiency;
end BatteryStorageTeachingModel;
