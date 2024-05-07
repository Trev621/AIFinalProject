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
        if line.startswith('Delivery algorithm:'):
            algorithm = line.split(':')[1].strip()
        elif line.startswith('Start location:'):
            startLocation = line.split(':')[1].strip()
        elif line.startswith('Delivery locations:'):
            deliveryLocations = [loc.strip() for loc in line.split(':')[1].split()]

    return algorithm, startLocation, deliveryLocations



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
        self.goal_pos = deliveryLocations

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
            self.goal_pos = tuple(map(int, goal_pos.split(',')))
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
            self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size, (x + 1) * self.cell_size, fill='green')
            current_cell = current_cell.parent

            # Redraw cell with updated g() and h() values
            self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size, (x + 1) * self.cell_size, fill=f'gray{color}')

            # Determine color for path gradient
            if idx % 200 > 100:
                color -= 2
            else:
                color += 2 
            idx += 4

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
    algorithm, startLocation, deliveryLocations = parse_input_file(args.filename)

    game = MazeGame(root, maze, algorithm, tuple(map(int, startLocation.split(','))), deliveryLocations) #top left to bottom right (1,6), (47,56)
    root.bind("<KeyPress>", game.move_agent)

    root.mainloop()



