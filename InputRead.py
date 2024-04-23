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
        if line.startswith('Delivery algorithm:'):
            algorithm = line.split(':')[1].strip()
        elif line.startswith('Start location:'):
            startLocation = line.split(':')[1].strip()
        elif line.startswith('Delivery locations:'):
            deliveryLocations = [loc.strip() for loc in line.split(':')[1].split(',')]

    return algorithm, startLocation, deliveryLocations

def find_path(algorithm, startLocation, deliveryLocations):
    if not algorithm or not startLocation or not deliveryLocations:
        return "Invalid Data"
    
    return f"Using {algorithm} from '{startLocation}' to {', '.join(deliveryLocations)}: path found."

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str)
    args = parser.parse_args()

    # Parse the input file
    algorithm, startLocation, deliveryLocations = parse_input_file(args.filename)

    # Find the path (mock implementation)
    result = find_path(algorithm, startLocation, deliveryLocations)

    # Print the result
    print(result)

main()
