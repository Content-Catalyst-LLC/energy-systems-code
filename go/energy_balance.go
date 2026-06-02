package main

import "fmt"

func sum(values []float64) float64 {
	result := 0.0
	for _, value := range values {
		result += value
	}
	return result
}

func main() {
	demand := []float64{42, 40, 38, 36, 35, 39, 48, 55, 61, 64, 66, 67}
	solar := []float64{0, 0, 0, 0, 2, 8, 18, 34, 48, 58, 62, 64}
	wind := []float64{18, 16, 15, 14, 16, 24, 30, 26, 22, 20, 18, 16}

	totalDemand := sum(demand)
	totalRenewable := 0.0
	for i := range demand {
		totalRenewable += solar[i] + wind[i]
	}

	fmt.Println("Go energy balance summary")
	fmt.Printf("Total demand: %.2f MWh\n", totalDemand)
	fmt.Printf("Total renewable generation: %.2f MWh\n", totalRenewable)
	fmt.Printf("Renewable share proxy: %.3f\n", totalRenewable/totalDemand)
}
