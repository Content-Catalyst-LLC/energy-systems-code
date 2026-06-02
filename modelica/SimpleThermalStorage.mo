model SimpleThermalStorage
  parameter Real capacity = 100 "Storage capacity in MWh";
  parameter Real chargeEfficiency = 0.9;
  parameter Real dischargeEfficiency = 0.9;
  Real stateOfCharge(start=20) "MWh";
  input Real chargePower "MW";
  input Real dischargePower "MW";
equation
  der(stateOfCharge) = chargeEfficiency * chargePower - dischargePower / dischargeEfficiency;
end SimpleThermalStorage;
