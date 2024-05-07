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
    size = deliveryQueue.qsize()
    tempQueue = PriorityQueue()
    #Put the contents of deliveryQueue into tempQueue and then puts them back
    for i in range(0, size):
        tempQueue.put(deliveryQueue.get())
    for i in range(0, size):
        deliveryQueue.put(tempQueue.get())    



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
from queue import Queue
class MazeGame:
    def __init__(self, root, maze, algorithm, startLocation, deliveryLocations):
        self.root = root
        self.maze = maze
        #Algorithm
        self.algorithm = algorithm
        self.original_start = startLocation
        #Initial Start State
        self.agent_pos = startLocation
        #List of reached locations
        self.location_list = [startLocation]
        self.deliveryLocations = deliveryLocations
        self.goal_queue = Queue()
        for loc in deliveryLocations:
            self.goal_queue.put(loc)
        
        #### Determine which algoithm to use
        if algorithm == "A*":
            self.A_Star = True
        elif algorithm == "Dijkstra's":
            self.A_Star = False
        else:
            print("Not a valid search algorithm: A* or Dijkstra's")

        #### The maze cell size in pixels
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.cell_size = 15
        self.canvas = tk.Canvas(root, width=self.cols * self.cell_size, height=self.rows * self.cell_size, bg='white')
        self.canvas.pack()

        self.colors = ['purple', 'blue', 'cyan', 'green', 'yellow', 'orange', 'magenta']
        self.colorIndex = 0

        self.draw_maze()
        self.mark_locations()
        self.process_next_goal()

    def process_next_goal(self):
        if not self.goal_queue.empty():
            goal_pos = self.goal_queue.get()
            self.prepare_path_finding(goal_pos)
            if not self.find_path():
                self.process_next_goal()
        else:
            self.print_results()
    
    #### Display the optimum path in the maze
    def prepare_path_finding(self, goal_pos):
        #### Reset all cells
        self.cells = [[Cell(x, y, self.maze[x][y] == 1) for y in range(self.cols)] for x in range(self.rows)]
        self.goal_pos = goal_pos
        #### Start state's initial values for f(n) = g(n) + h(n) 
        self.cells[self.agent_pos[0]][self.agent_pos[1]].g = 0
        self.cells[self.agent_pos[0]][self.agent_pos[1]].h = self.heuristic(self.agent_pos, A_Star=self.algorithm == "A*")
        self.cells[self.agent_pos[0]][self.agent_pos[1]].f = self.heuristic(self.agent_pos, A_Star=self.algorithm == "A*")

    ############################################################
    #### Draw the maze
    ############################################################
    def draw_maze(self):
        for x in range(self.rows):
            for y in range(self.cols):
                ward = self.maze[x][y]
                color = 'black' if ward == 1 else 'gray' if ward == 2 else 'tomato' if ward == 3 else 'light goldenrod' if ward == 4 else 'sky blue' if ward == 5 else 'pink' if ward == 6 else 'forest green' if ward == 7 else 'orange' if ward == 8 else 'teal' if ward == 9 else 'light green' if ward == 10 else 'violet' if ward == 11 else 'coral' if ward == 12 else 'lime' if ward == 13 else 'white'
                self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size, (x + 1) * self.cell_size, fill=color)

    # Marks delivery locations on the maze
    def mark_locations(self):
        self.canvas.create_rectangle(self.location_list[0][1] * self.cell_size, self.location_list[0][0] * self.cell_size, (self.location_list[0][1] + 1) * self.cell_size, (self.location_list[0][0] + 1) * self.cell_size, fill=f'green4')
        for location in self.deliveryLocations:
            self.canvas.create_rectangle(location[1] * self.cell_size, location[0] * self.cell_size, (location[1] + 1) * self.cell_size, (location[0] + 1) * self.cell_size, fill=f'brown4')

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
        found_path = False

        #### Continue exploring until the queue is exhausted
        while not open_set.empty():
            _, current_pos = open_set.get()
            #### Stop if goal is reached
            if current_pos == self.goal_pos:
                self.location_list.append(current_pos)
                self.reconstruct_path(current_pos)
                found_path = True
                break
            #### Agent goes E, W, N, and S, whenever possible
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_pos = (current_pos[0] + dx, current_pos[1] + dy)
                if self.is_valid(new_pos):
                    new_g = self.cells[current_pos[0]][current_pos[1]].g + 1
                    if new_g < self.cells[new_pos[0]][new_pos[1]].g:
                        self.update_cell(new_pos, current_pos, new_g)
                        open_set.put((self.cells[new_pos[0]][new_pos[1]].f, new_pos))

        if current_pos != self.goal_pos:
            print(f"Unable to access location {self.goal_pos}")
            
        return found_path
    
    def update_cell(self, new_pos, current_pos, new_g):
        new_x, new_y = new_pos
        ### Update the path cost g()
        self.cells[new_x][new_y].g = new_g
        ### Update the heurstic h()
        self.cells[new_x][new_y].h = self.heuristic(new_pos, A_Star=self.algorithm == "A*")
        ### Update the evaluation function for the cell n: f(n) = g(n) + h(n)
        self.cells[new_x][new_y].f = self.cells[new_x][new_y].g + self.cells[new_x][new_y].h
        self.cells[new_x][new_y].parent = self.cells[current_pos[0]][current_pos[1]]
    
    def is_valid(self, pos):
        x, y = pos
        return 0 <= x < self.rows and 0 <= y < self.cols and not self.cells[x][y].is_wall
    
    def setup_and_find_path(self, goal_pos):
        self.goal_pos = goal_pos
        self.cells = [[Cell(x, y, self.maze[x][y] == 1) for y in range(self.cols)] for x in range(self.rows)]
        self.cells[self.agent_pos[0]][self.agent_pos[1]].g = 0
        self.cells[self.agent_pos[0]][self.agent_pos[1]].h = self.heuristic(self.agent_pos, A_Star=self.A_Star)
        self.cells[self.agent_pos[0]][self.agent_pos[1]].f = self.heuristic(self.agent_pos, A_Star=self.A_Star)
        self.find_path()
                        
    ############################################################
    #### Construct the found path
    ############################################################
    def reconstruct_path(self, goal_pos):
        path = []
        current_pos = goal_pos
        while self.cells[current_pos[0]][current_pos[1]].parent is not None:
            path.append(current_pos)
            parent_cell = self.cells[current_pos[0]][current_pos[1]].parent
            current_pos = (parent_cell.x, parent_cell.y)
        path.reverse()
        self.update_locations()
        self.draw_path(path, 0)

    #Marks delivery locations on the maze
    def update_locations(self):
        self.canvas.create_rectangle(self.location_list[-1][1] * self.cell_size, self.location_list[-1][0] * self.cell_size, (self.location_list[-1][1] + 1) * self.cell_size, (self.location_list[-1][0] + 1) * self.cell_size, fill=f'blue')

    #Draws the path, each step takes 50ms
    def draw_path(self, path, index):
        if index < len(path):
            x, y = path[index]
            self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size, (x + 1) * self.cell_size, fill=self.colors[self.colorIndex])
            self.root.after(50, lambda: self.draw_path(path, index + 1))
        else:
            #When path is fully drawn, update agent_pos and process the next goal
            self.agent_pos = path[-1]
            self.update_locations()
            self.colorIndex = (self.colorIndex + 1) % len(self.colors) #Change color of path
            self.root.after(100, self.process_next_goal)

    ############################################################
    #### Print results
    ############################################################
    def print_results(self):
        if self.location_list.__len__() > 1:
            print(f"Successfully delivered to {self.location_list[1:]}")
        else:
            print("No packages successfully delivered")
        print("============================================================")
        print("")

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
    if isinstance(result, tuple) and len(result) == 3 and maze[result[1][0]][result[1][1]] != 1 and result[2].count(result[1]) == 0:
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
        root.bind("<KeyPress>", game.move_agent)
        root.mainloop()

    # Check for if starting value is a wall
    elif isinstance(result, tuple) and len(result) == 3 and maze[result[1][0]][result[1][1]] == 1:
        print("---------------------------------------------------")
        print("Starting location cannot be a wall")
        print("---------------------------------------------------")

    # Check for if starting value is the same as a goal
    elif isinstance(result, tuple) and len(result) == 3 and result[2].count(result[1]) != 0:
        print("---------------------------------------------------")
        print("Starting location cannot be a goal")
        print("---------------------------------------------------")
        
    # Handle error or unexpected return values
    else:
        print("---------------------------------------------------")
        print(result)
        print("---------------------------------------------------")