#!/usr/bin/env python3
from grid_reliability import OutageEvent, caidi, saidi, saifi

events = [
    OutageEvent(10000, 2.0),
    OutageEvent(5000, 4.0),
    OutageEvent(20000, 1.0),
]

customers = 100000

print("SAIDI", saidi(events, customers))
print("SAIFI", saifi(events, customers))
print("CAIDI", caidi(events, customers))
