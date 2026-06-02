package main

import "fmt"

type Household struct {
	ID     string
	Income float64
	Cost   float64
}

func main() {
	households := []Household{
		{"H001", 22000, 3100},
		{"H002", 36000, 2800},
		{"H003", 52000, 2600},
	}

	fmt.Println("household_id,energy_burden")
	for _, h := range households {
		fmt.Printf("%s,%.3f\n", h.ID, h.Cost/h.Income)
	}
}
