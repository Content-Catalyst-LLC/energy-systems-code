% MATLAB/Octave-compatible demand response teaching model

demand = [420 405 395 390 410 455 520 590 635 660 675 690 705 725 740 755 780 800 775 720 660 590 520 465];
threshold = 700;
max_shift_fraction = 0.08;

adjusted = demand;
for i = 1:length(demand)
    if demand(i) > threshold
        reduction = min(demand(i) - threshold, demand(i) * max_shift_fraction);
        adjusted(i) = demand(i) - reduction;
    end
end

disp("hour,original_demand_mwh,adjusted_demand_mwh")
for i = 1:length(demand)
    fprintf("%d,%.2f,%.2f\n", i, demand(i), adjusted(i));
end
