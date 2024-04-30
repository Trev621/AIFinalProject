import argparse
import re

def parse_input_file(filename):
    with open(filename, 'r') as file:
        data = file.readlines()
    
    algorithm = None
    startLocation = None
    deliveryLocations = []

    for line in data:
        line = line.strip()
        #Checks for correct formatting of input
        if line.startswith('Delivery algorithm:'):
            algorithm = line.split(':')[1].strip()
        elif line.startswith('Start location:'):
            try:
                startLocation = tuple(map(int, line.split(':')[1].strip().split(',')))
            except ValueError:
                return "Invalid Starting Location Format"
        elif line.startswith('Delivery locations:'):
            locations = line.split(':', 1)[1].strip()
            try:
                deliveryLocations = [tuple(map(int, loc.strip().split(','))) for loc in locations.split()]
            except ValueError:
                return "Invalid Delivery Locations Format"
    
    #Checks the value of data and makes sure it is within the correct ranges
    if not algorithm or checkAlgorithm(algorithm) == False:
        return "Invalid Algorithm, enter A* or Dijkstra's"
    if not startLocation or checkStartingValues(startLocation) == False:
        return "Invalid Starting Location, enter coordinates"
    if not deliveryLocations or checkDeliveryLocations(deliveryLocations) == False:
        return "Invalid Delivery Locations, enter pairs of coordinates separated by spaces"
    
    return algorithm, startLocation, deliveryLocations

#Returns true if the algorithm entered is A* or Dijkstra's
def checkAlgorithm(algorithm):
    if algorithm == "A*" or algorithm == "a*" or algorithm == "Dijkstra's" or algorithm == "dijkstra's":
        return True
    return False

#Returns true if the starting tuple contains two numbers where first is between 0 and 47 and second is between 0 and 60
def checkStartingValues(startLocation):
    if not isinstance(startLocation, tuple) or len(startLocation) != 2:
        return False
    first, second = startLocation
    if (isinstance(first, (int, float)) and isinstance(second, (int, float))):
        return (0 <= first <= 47) and (0 <= second <= 60)
    return False

#Returns true if each tuple in delivery locations contains a number where first is between 0 and 47 and second is between 0 and 60
def checkDeliveryLocations(deliveryLocations):
    return all(checkStartingValues(locations) for locations in deliveryLocations)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str)
    args = parser.parse_args()

    # Parse the input file
    result = parse_input_file(args.filename)

    # Check if the returned result is a tuple of three elements
    if isinstance(result, tuple) and len(result) == 3:
        algorithm, startLocation, deliveryLocations = result
        print("Algorithm:", algorithm)
        print("Start Location:", startLocation)
        print("Delivery Locations:", deliveryLocations)
    else:
        # Handle error or unexpected return values
        print(result)

main()
