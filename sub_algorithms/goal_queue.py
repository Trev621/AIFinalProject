from queue import PriorityQueue
import numpy as np

#maze as an array
maze = np.array([
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
[0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0]])

#Initialize start and goals for testing purposes
#start = 15,15
goals = ((47, 56), (13, 59), (26, 21), (1, 18), (46, 20), (11, 50), (7, 27))
#goals2 = np.array([maze[7][10], maze[46][14], maze[46][7], maze[15][53]])
#print(goals)
#print(goals2)

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
    
    


#Testing cases

#Calls create_goal_queue function
#queue1 = create_goal_queue(maze, goals)
#Prints the queue for testing purposes
#queue1.queue[2] = (0, 12)
#temp = queue1.get()
#queue1.put(temp)
#while not queue1.empty():
    #print(queue1.get())

queue2 = create_goal_queue(maze, goals)
start = (46,16)
#queue2.queue[0] = (2,(45,51))
print(queue2.queue)

print("start ward: " + str(maze[start[0],start[1]]))
print("location wards: ")
for i in (range(goals.__len__())):
    print(maze[queue2.queue[i][1][0],queue2.queue[i][1][1]])

check_ward(maze,start,queue2)
while not queue2.empty():
    print(queue2.get())



