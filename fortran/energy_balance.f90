program energy_balance
  implicit none
  real :: demand(12), solar(12), wind(12)
  real :: total_demand, total_renewable
  integer :: i

  demand = (/42, 40, 38, 36, 35, 39, 48, 55, 61, 64, 66, 67/)
  solar =  (/0, 0, 0, 0, 2, 8, 18, 34, 48, 58, 62, 64/)
  wind =   (/18, 16, 15, 14, 16, 24, 30, 26, 22, 20, 18, 16/)

  total_demand = sum(demand)
  total_renewable = 0.0

  do i = 1, 12
    total_renewable = total_renewable + solar(i) + wind(i)
  end do

  print *, "Fortran energy balance summary"
  print *, "Total demand MWh:", total_demand
  print *, "Total renewable generation MWh:", total_renewable
  print *, "Renewable share proxy:", total_renewable / total_demand
end program energy_balance
