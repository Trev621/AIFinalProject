#######################################################
#### Final Project
#### Joe Popp, Trevor, Deston
#### AI, Spring 2024
#######################################################
import tkinter as tk
from PIL import ImageTk, Image, ImageOps 
from queue import PriorityQueue
import argparse
import re



######################################################
#### Read file 
######################################################
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



######################################################
#### Create ordered queue
######################################################
#Define create_goal_queue function to put all of the goals in the queue
def create_goal_queue(maze,deliveryLocations):
    queue = PriorityQueue()
    #Assigns priority based on ward number and adds location to queue
    for i in range(len(deliveryLocations)):
        if (maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==4 or maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==7 
            or maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==8 or maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==11):
            queue.put((1,deliveryLocations[i]))
        elif (maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==5 or maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==6):
            queue.put((2,deliveryLocations[i]))
        elif (maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==10 or maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==12):
            queue.put((3,deliveryLocations[i]))
        elif (maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==3 or maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==13):
            queue.put((4,deliveryLocations[i]))
        elif (maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==2 or maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==9):
            queue.put((5,deliveryLocations[i]))
        elif (maze[deliveryLocations[i][0]][deliveryLocations[i][1]]==1):
            print("Location", deliveryLocations[i], "is inside a wall.")
        else:
            print("Location", deliveryLocations[i], "is not inside a ward.")
    return queue


#Function that checks if current location is the same as any locations in the queue and moves any it finds to the front of the queue
def check_ward(maze, startLocation, deliveryQueue):
    for i in range(0, deliveryQueue.qsize()):
        #If start ward is same as ith ward in queue
        if (maze[deliveryQueue.queue[i][1][0]][deliveryQueue.queue[i][1][1]] == maze[startLocation[0]][startLocation[1]]):
            #Give it highest priority
            deliveryQueue.queue[i] = (0, deliveryQueue.queue[i][1])
    #This reorginizes the queue so it's in the correct order
    temp = deliveryQueue.get()
    deliveryQueue.put(temp)
    temp = deliveryQueue.get()
    deliveryQueue.put(temp)



######################################################
#### Cell class
######################################################
class Cell:
    #### Initially, arre maze cells have g() = inf and h() = 0
    def __init__(self, x, y, is_wall=False):
        self.x = x
        self.y = y
        self.is_wall = is_wall
        self.g = float("inf")
        self.h = 0
        self.f = float("inf")
        self.parent = None

    #### Compare two cells based on their evaluation functions
    def __lt__(self, other):
        return self.f < other.f



######################################################
#### Maze class
######################################################
class MazeGame:
    def __init__(self, root, maze, algorithm, startLocation, deliveryLocations):
        self.root = root
        self.maze = maze
        
        #### Determine which algoithm to use
        if algorithm == "A*":
            self.A_Star = True
        elif algorithm == "Dijkstra's":
            self.A_Star = False
        else:
            print("Not a valid search algorithm: A* or Dijkstra's")

        self.rows = len(maze)
        self.cols = len(maze[0])

        #### Initial start state:       
        self.agent_pos = startLocation
        
        #### Goal states: 
        self.deliveryLocations = deliveryLocations

        #### List of successfully reached locations
        self.location_list = [startLocation]

        #### The maze cell size in pixels
        self.cell_size = 15
        self.canvas = tk.Canvas(root, width=self.cols * self.cell_size, height=self.rows * self.cell_size, bg='white')
        self.canvas.pack()

        self.draw_maze()
        
        #### Display the optimum path in the maze
        for goal_pos in deliveryLocations:
            #### Reset all cells
            self.cells = [[Cell(x, y, maze[x][y] == 1) for y in range(self.cols)] for x in range(self.rows)]

            #### Start state's initial values for f(n) = g(n) + h(n) 
            self.goal_pos = goal_pos
            self.cells[self.agent_pos[0]][self.agent_pos[1]].g = 0
            self.cells[self.agent_pos[0]][self.agent_pos[1]].h = self.heuristic(self.agent_pos, A_Star=self.A_Star)
            self.cells[self.agent_pos[0]][self.agent_pos[1]].f = self.heuristic(self.agent_pos, A_Star=self.A_Star)

            #### Find all paths
            self.find_path()
            self.agent_pos = self.location_list[-1]  

        self.print_results()          

    ############################################################
    #### Draw the maze
    ############################################################
    def draw_maze(self):
        for x in range(self.rows):
            for y in range(self.cols):
                ward = self.maze[x][y]
                color = 'black' if ward == 1 else 'tomato' if ward == 9 else 'tomato' if ward == 2 else 'light goldenrod' if ward == 3 else 'light goldenrod' if ward == 13 else 'pale green' if ward == 12 else 'pale green' if ward == 10 else 'sky blue' if ward == 5 else 'sky blue' if ward == 6 else 'medium purple' if ward == 11 else 'medium purple' if ward == 4 else 'medium purple' if ward == 8 else 'medium purple' if ward == 7 else 'white'
                self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size, (x + 1) * self.cell_size, fill=color)

    ############################################################
    #### Determine heuristic
    ############################################################
    def heuristic(self, pos, A_Star=True):
        if A_Star:
            return (abs(pos[0] - self.goal_pos[0]) + abs(pos[1] - self.goal_pos[1]))
        else:
            return 0

    ############################################################
    #### Path Algorithm
    ############################################################
    def find_path(self):
        open_set = PriorityQueue()
        
        #### Add the start state to the queue
        open_set.put((0, self.agent_pos))

        #### Continue exploring until the queue is exhausted
        while not open_set.empty():
            current_cost, current_pos = open_set.get()
            current_cell = self.cells[current_pos[0]][current_pos[1]]

            #### Stop if goal is reached
            if current_pos == self.goal_pos:
                self.location_list.append(current_pos)
                self.reconstruct_path()
                break

            #### Agent goes E, W, N, and S, whenever possible
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_pos = (current_pos[0] + dx, current_pos[1] + dy)

                if 0 <= new_pos[0] < self.rows and 0 <= new_pos[1] < self.cols and not self.cells[new_pos[0]][new_pos[1]].is_wall:
                
                    #### The cost of moving to a new position is 1 unit
                    new_g = current_cell.g + 1
                    
                    if new_g < self.cells[new_pos[0]][new_pos[1]].g:
                        ### Update the path cost g()
                        self.cells[new_pos[0]][new_pos[1]].g = new_g
                        
                        ### Update the heurstic h()
                        self.cells[new_pos[0]][new_pos[1]].h = self.heuristic(new_pos, A_Star=self.A_Star)
                        
                        ### Update the evaluation function for the cell n: f(n) = g(n) + h(n)
                        self.cells[new_pos[0]][new_pos[1]].f = new_g + self.cells[new_pos[0]][new_pos[1]].h
                        self.cells[new_pos[0]][new_pos[1]].parent = current_cell
                        
                        #### Add the new cell to the priority queue
                        open_set.put((self.cells[new_pos[0]][new_pos[1]].f, new_pos))

        if current_pos != self.goal_pos:
            print(f"Unable to access location {self.goal_pos}")
                        
    ############################################################
    #### Construct the found path
    ############################################################
    def reconstruct_path(self):
        current_cell = self.cells[self.goal_pos[0]][self.goal_pos[1]]
        idx = 1
        color = 20
        while current_cell.parent:
            x, y = current_cell.x, current_cell.y
            current_cell = current_cell.parent

            # Draw path
            self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size, (x + 1) * self.cell_size, fill=f'gray{color}')

            # Determine color for path gradient
            if idx % 200 > 100:
                color -= 2
            else:
                color += 2 
            idx += 4

        # Highlight goals
        for location in self.deliveryLocations:
            self.canvas.create_rectangle(location[1] * self.cell_size, location[0] * self.cell_size, (location[1] + 1) * self.cell_size, (location[0] + 1) * self.cell_size, fill=f'brown4')
        for location in self.location_list:
            self.canvas.create_rectangle(location[1] * self.cell_size, location[0] * self.cell_size, (location[1] + 1) * self.cell_size, (location[0] + 1) * self.cell_size, fill=f'blue')
        self.canvas.create_rectangle(self.location_list[0][1] * self.cell_size, self.location_list[0][0] * self.cell_size, (self.location_list[0][1] + 1) * self.cell_size, (self.location_list[0][0] + 1) * self.cell_size, fill=f'green4')

    ############################################################
    #### Print results
    ############################################################
    def print_results(self):
        if self.location_list.__len__() > 1:
            print(f"Successfully delivered to {self.location_list[1:]}")
        else:
            print("No packages successfully delivered")

    ############################################################
    #### Moving mechanics
    ############################################################
    def move_agent(self, event):
    
        #### Move right, if possible
        if event.keysym == 'Right' and self.agent_pos[1] + 1 < self.cols and not self.cells[self.agent_pos[0]][self.agent_pos[1] + 1].is_wall:
            self.agent_pos = (self.agent_pos[0], self.agent_pos[1] + 1)


        #### Move Left, if possible            
        elif event.keysym == 'Left' and self.agent_pos[1] - 1 >= 0 and not self.cells[self.agent_pos[0]][self.agent_pos[1] - 1].is_wall:
            self.agent_pos = (self.agent_pos[0], self.agent_pos[1] - 1)
        
        #### Move Down, if possible
        elif event.keysym == 'Down' and self.agent_pos[0] + 1 < self.rows and not self.cells[self.agent_pos[0] + 1][self.agent_pos[1]].is_wall:
            self.agent_pos = (self.agent_pos[0] + 1, self.agent_pos[1])
   
        #### Move Up, if possible   
        elif event.keysym == 'Up' and self.agent_pos[0] - 1 >= 0 and not self.cells[self.agent_pos[0] - 1][self.agent_pos[1]].is_wall:
            self.agent_pos = (self.agent_pos[0] - 1, self.agent_pos[1])

        #### Erase agent from the previous cell at time t
        self.canvas.delete("agent")

        
        ### Redraw the agent in color navy in the new cell position at time t+1
        self.canvas.create_rectangle(self.agent_pos[1] * self.cell_size, self.agent_pos[0] * self.cell_size, 
                                    (self.agent_pos[1] + 1) * self.cell_size, (self.agent_pos[0] + 1) * self.cell_size, 
                                    fill='navy', tags="agent")

                  

############################################################
#### Initializa maze object
############################################################
maze = [
    [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,5,5,5,5,5,1,5,5,1,5,5,5,5,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,5,5,5,5,5,5,5,5,1,5,5,5,5,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,5,5,5,5,5,1,5,5,1,5,5,5,5,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,5,5,5,5,5,1,5,5,5,5,5,5,5,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,5,5,5,5,5,1,1,5,1,5,5,5,5,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,1,1,1,1,5,1,5,5,1,5,1,5,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,5,5,1,5,5,5,5,5,5,5,5,5,1,3,3,3,1,3,3,3,1,3,3,3,3,1,3,3,1,3,3,3,3,3,1,3,3,1,3,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,5,5,5,5,1,5,1,1,1,5,1,1,1,1,3,3,1,3,3,3,1,3,3,3,3,1,3,3,1,3,3,3,1,1,1,3,3,1,3,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,1,1,1,5,1,5,1,5,5,5,5,5,5,1,3,3,1,3,3,3,1,3,3,3,3,1,3,3,1,3,3,3,1,3,1,3,3,1,3,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,5,5,5,0,1,5,1,5,1,3,1,5,5,1,3,3,1,3,3,3,1,3,3,3,3,1,3,1,1,3,1,1,1,3,1,3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,1,1,1,0,1,1,1,1,1,3,1,1,1,1,3,3,1,1,3,3,1,1,3,3,1,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0,0,0,1,4,4,1,4,4,4,1,2,2,2,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0,0,0,1,1,1,1,4,4,4,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,1,9,1,1,3,1,1,1,3,1,1,1,3,3,3,3,3,3,1,1,1,1,3,1,3,1,3,1,3,3,1,3,1,1,3,1,1,1,1,0,0,4,4,4,1,4,4,4,1,2,2,2,1],
    [1,0,0,0,0,0,0,0,1,9,9,1,3,3,3,1,3,3,1,3,3,3,3,3,3,3,1,3,3,1,3,1,3,1,3,1,3,3,1,3,3,1,3,3,1,9,9,0,0,1,1,1,1,4,4,4,1,2,2,2,1],
    [1,0,0,0,0,0,0,0,1,1,1,1,1,3,3,1,1,1,1,3,3,3,3,3,3,3,3,3,3,1,3,1,3,1,1,1,3,3,1,3,3,1,3,3,1,1,1,0,0,4,4,4,1,4,4,4,1,2,2,2,1],
    [1,0,0,0,0,0,0,0,0,1,2,2,1,3,3,1,3,3,1,3,3,3,3,3,3,3,1,3,3,1,3,1,3,1,3,1,3,3,1,3,3,1,3,3,1,9,1,0,0,1,1,1,1,4,4,4,1,1,2,1,1],
    [1,0,0,0,0,0,0,0,1,1,1,2,1,3,1,1,1,3,1,1,3,3,3,3,3,3,1,1,1,1,3,1,3,1,3,1,3,3,1,3,3,1,3,3,1,9,1,0,0,4,4,4,1,4,4,4,1,2,2,2,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,9,1,0,0,1,1,1,1,4,4,4,1,2,2,2,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,4,4,1,9,9,9,9,1,0,0,4,4,4,4,4,4,4,1,2,2,2,1],
    [1,0,0,0,0,0,0,0,0,1,0,1,0,1,1,0,1,3,1,3,1,3,3,1,3,1,11,1,3,1,3,1,1,3,1,1,3,3,1,4,4,1,9,9,9,9,9,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,1,0,0,1,0,1,0,0,1,3,1,3,1,3,3,1,3,1,11,1,3,1,3,3,1,3,3,1,3,3,4,4,4,1,1,1,1,1,1,0,0,1,8,8,1,2,1,2,2,2,2,2,1],
    [1,0,0,0,0,0,0,0,1,0,0,1,0,1,0,0,1,3,1,3,1,3,3,1,3,1,11,1,1,1,3,3,1,3,3,1,3,3,1,1,1,1,0,1,4,4,1,0,0,1,8,8,1,2,2,2,2,2,2,2,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,11,11,11,1,1,1,1,1,1,1,3,3,1,4,4,1,0,1,1,4,4,0,0,1,1,8,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,11,11,11,11,11,11,11,11,11,11,11,1,11,11,1,3,3,3,3,3,3,3,4,4,4,1,0,0,1,1,1,0,0,8,8,8,8,8,8,8,8,8,8,8,1],
    [1,0,0,0,0,1,0,0,1,0,0,1,0,1,0,1,11,11,1,1,1,11,11,11,11,11,11,1,1,1,1,1,1,3,3,1,3,3,1,1,1,1,0,0,0,0,1,0,0,1,1,8,1,8,8,8,8,8,1,8,1],
    [1,0,0,0,0,0,0,0,1,0,0,1,0,1,0,1,11,11,11,11,1,11,11,11,11,11,11,1,3,3,3,3,3,3,3,1,0,0,1,9,9,1,0,0,1,0,1,0,0,1,8,8,1,8,8,8,8,8,1,8,1],
    [1,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,9,1,0,1,1,1,1,0,0,1,1,1,1,8,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,8,8,8,8,8,8,8,8,8,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,8,8,8,8,8,8,8,8,1],
    [1,1,1,1,1,1,0,0,0,0,1,9,1,1,1,0,1,1,1,2,1,2,1,1,1,1,1,1,12,1,1,1,1,1,1,1,0,0,1,1,1,6,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,0,1,0,0,0,0,1,1,1,0,1,0,1,2,2,2,1,2,2,2,1,12,12,12,12,12,12,12,12,12,12,1,0,0,1,6,6,6,6,6,1,7,1,0,0,1,7,7,7,1,7,7,7,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,1,0,0,0,1,0,1,1,1,1,1,2,2,2,1,12,1,1,12,12,12,12,1,12,12,1,0,0,1,6,1,1,6,1,1,7,7,7,7,1,7,7,7,1,7,7,7,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,1,1,1,1,1,12,12,12,12,12,12,1,1,1,1,0,0,6,6,1,6,6,6,1,1,1,7,7,1,7,1,1,1,7,7,7,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,10,10,1,12,12,1,1,12,12,12,12,1,10,10,0,0,0,1,6,6,6,6,6,1,7,7,7,7,7,7,7,7,7,7,7,7,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,1,1,1,1,1,0,1,0,0,0,1,10,10,1,12,12,12,12,12,12,12,12,1,10,1,1,0,0,1,1,1,6,1,1,1,1,1,7,7,7,7,7,7,7,7,7,7,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,1,1,1,1,1,10,1,1,1,1,1,1,1,1,1,1,1,1,10,0,0,1,6,6,6,1,6,1,7,7,7,7,7,7,7,7,7,7,7,7,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,10,10,1,10,10,10,10,10,10,10,1,10,10,1,10,1,10,10,1,0,0,1,1,1,6,1,6,1,1,1,7,7,7,7,7,7,1,7,1,7,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,10,10,1,10,1,10,10,10,10,10,1,10,10,1,10,1,10,10,1,0,0,6,6,1,6,1,6,1,7,7,7,7,1,1,1,1,1,7,1,7,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,1,1,1,1,1,1,1,1,10,1,1,1,10,10,10,10,10,1,10,1,1,10,1,10,1,1,0,0,1,6,1,6,1,6,1,1,1,1,1,1,6,6,6,1,1,1,1,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6,6,6,6,6,6,6,6,6,6,6,6,1,6,1,6,6,6,1,0,0,0],
    [0,0,0,0,0,1,0,0,1,1,0,1,1,1,10,1,10,1,10,1,1,10,1,1,10,1,1,10,1,1,10,1,1,10,1,10,1,10,1,1,6,6,1,13,1,6,1,1,13,1,6,1,1,1,6,1,1,1,0,0,0],
    [0,0,0,0,0,1,0,0,1,0,0,1,10,1,10,10,10,1,10,1,10,1,10,1,10,1,10,10,1,10,1,10,1,10,1,10,1,10,1,6,6,6,1,13,1,1,1,13,13,1,6,6,6,6,6,6,6,1,0,0,0],
    [0,0,0,0,0,1,0,0,1,1,1,1,10,10,10,1,1,1,10,10,10,1,10,10,10,1,10,10,10,10,1,10,10,10,1,1,1,10,1,6,6,6,1,13,13,1,13,13,13,1,6,6,6,6,6,6,6,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,0,1,1,1,10,10,10,1,10,1,1,1,1,1,10,1,10,10,1,1,1,1,1,10,1,10,10,10,1,6,6,6,1,13,13,1,13,13,13,1,6,6,6,6,6,6,6,1,0,0,0],
    [0,0,0,0,0,1,1,9,1,9,1,1,10,10,10,10,10,1,10,10,10,1,10,10,10,1,10,10,10,10,1,10,10,10,1,10,10,10,1,6,6,6,1,13,13,1,1,1,1,1,6,6,6,6,6,6,6,1,0,0,0],
    [0,0,0,0,0,1,9,9,1,9,9,1,10,10,10,10,10,1,10,10,10,1,10,10,10,1,10,10,10,10,1,10,10,10,1,10,10,10,1,6,6,6,1,13,13,13,13,13,13,1,6,6,6,6,6,6,6,1,0,0,0],
    [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0]
]



############################################################
#### Main
############################################################
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Maze")

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str)
    args = parser.parse_args()

    # Parse the input file
    result = parse_input_file(args.filename)

    # Check if the returned result is a tuple of three elements
    if isinstance(result, tuple) and len(result) == 3:
        algorithm, startLocation, deliveryLocations = result
        print("")
        print("============================================================")
        print("Algorithm:", algorithm)
        print("Start Location:", startLocation)
        print("Delivery Locations:", deliveryLocations)
        print("------------------------------------------------------------")

        # Organize the queue
        deliveryQueue = create_goal_queue(maze, deliveryLocations)
        check_ward(maze, startLocation, deliveryQueue)
        deliveryLocations = []
        while not deliveryQueue.empty():
            deliveryLocations.append(deliveryQueue.get()[1])
        print("Reordered Queue:", deliveryLocations)
        print("------------------------------------------------------------")

        # Run the algorithm
        game = MazeGame(root, maze, algorithm, startLocation, deliveryLocations) #top left to bottom right (1,6), (47,56)
        print("============================================================")
        print("")
        root.bind("<KeyPress>", game.move_agent)
        root.mainloop()
    else:
        # Handle error or unexpected return values
        print("---------------------------------------------------")
        print(result)
        print("---------------------------------------------------")