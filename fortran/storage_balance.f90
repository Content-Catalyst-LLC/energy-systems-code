program storage_balance
  implicit none

  integer, parameter :: n = 8
  real(8) :: demand(n), renewables(n), soc, capacity, eff, net
  integer :: i

  demand = (/420.0d0, 405.0d0, 395.0d0, 390.0d0, 410.0d0, 455.0d0, 520.0d0, 590.0d0/)
  renewables = (/165.0d0, 172.0d0, 168.0d0, 160.0d0, 155.0d0, 165.0d0, 215.0d0, 298.0d0/)
  soc = 300.0d0
  capacity = 720.0d0
  eff = 0.94d0

  print *, "hour,state_of_charge_mwh"
  do i = 1, n
     net = renewables(i) - demand(i)
     if (net >= 0.0d0) then
        soc = min(capacity, soc + net * eff)
     else
        soc = max(0.0d0, soc - abs(net) / eff)
     end if
     print *, i, soc
  end do
end program storage_balance
