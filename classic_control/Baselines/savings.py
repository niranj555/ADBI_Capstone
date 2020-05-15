import pandas as pd 
import numpy as np
import operator
from audioop import reverse
from itertools import repeat
import router
import math

'''
 savings algorithm:
 calculate savings:
 s(i, j) = d(D, i) + d(D, j) - d(i, j) for every pair (i, j) of demand points D = depot
 include link (i,j) in route if no route constraints violated with inclusion of (i,j) as route
 AND if either:

      a. Either, neither i nor j have already been assigned to a route, in which case a new route is initiated including both i and j.

      b. Or, exactly one of the two points (i or j) has already been included in an existing route and that point is not interior to 
      that route (a point is interior to a route if it is not adjacent to the depot D in the order of traversal of points), in which 
      case the link (i, j) is added to that same route.

      c. Or, both i and j have already been included in two different existing routes and neither point is interior to its route, 
      in which case the two routes are merged.

if savings list still not exhausted, return to previous step and process next entry
otherwise, stop
'''

def calculate_savings(dm):
    savings = dict()
    for i in range(1,len(dm)):
        for j in range(1,len(dm[i])):
            savings[i] =[j, dm[0][i] + dm[0][j] - dm[i][j]]
            savings[j] =[i, dm[0][i] + dm[0][j] - dm[i][j]]

    return savings

def create_data_model(r):
    """Stores the data for the problem."""
    distance_matrix = r.adj_matrix(r.gen_adj())
    demands = r.get_demand()

    return distance_matrix, demands

fn = 'instances/my2.txt'
r = router.Router(fn)
stops = r.get_stops()
students = r.get_students()
maxwalk = r.get_maxwalk()
capacity = r.get_capacity()
student_near_stops = r.get_student_near_stops()
stopPosDemand = dict()
noStops = len(stops)-1 

dist_matrix, demands = create_data_model(r)
stops_w = stops.copy()
del stops[0]
savings = calculate_savings(dist_matrix)

for i in range(len(stops)):
    stopPosDemand[i] = demands[i]

stopsPositions = list(stopPosDemand.keys())
stopsLen = len(stops) # num of stops
depot = 0

# STEP 1
distanceDict = dist_matrix
'''
for i in range(stopsLen):
    for j in range(i+1, stopsLen):
        distanceDict[(stopsPositions[i], stopsPositions[j])] = np.linalg.norm(stops[stopsPositions[i]]-stops[stopsPositions[j]])
'''

# STEP 2 
# savings is already calculated

savings = sorted(savings.items(), key = operator.itemgetter(1), reverse = True)
l = len(savings)
stop_pairs = list()
for i in range(1,l):
    stop_pairs.append((i,savings[i][0]))

# initially no stop has been visited
stopVisited = dict()
for c in stopsPositions:
    stopVisited[c] = False

# STEP 3 
def inPrevious(new, existing):
    start = existing[0]
    end = existing[len(existing)-1]
    if new == start:
        return 1
    elif new == end:
        return 0
    else:
        return -1

def capacityValid(existing, new):
    totalCap = stopPosDemand[new]
    for c in existing:
        totalCap += stopPosDemand[c]

    return totalCap <= capacity

def isServed(c):
    return stopVisited[c]

def hasBeenServed(c):
    stopVisited[c] = True

def allStopsCons(stopV): 
    for v in stopV.values():
        if v == False:
            return False
    return True

def euclideanDistance( xy1, xy2 ):
    "Returns the Euclidean distance between points xy1 and xy2"
    return  math.sqrt(( stops_w[xy2][0] - stops_w[xy1][0] )**2 + ( stops_w[xy2][1] - stops_w[xy1][1] )**2) ############################### FIX THIS

def calculateRouteCost(r):
    total = 0
    print(r)
    print(stops_w[0])
    for i in range(len(r)-1):
        print("In final route")
        print(r[i])
        total+= euclideanDistance(r[i] , r[i+1]) 
    return total

# Algorithm
route = dict()

l = len(stop_pairs)
print("THIS IS STOP PAIRS: ")
print(stop_pairs)
i = 0
idx = -1
bus = [0,0,0,0,0]

#allStopsCons(stopVisited)
while ( list(stopVisited.values()) == [False]* len(stopVisited)):
    # choosing maximum savings customers who are unserved
    # visiting in pairs: visited[i] = true, visited[j] = true
    for c in stop_pairs:
        if (stopVisited[c[0]] == False and stopVisited[c[1]] == False):
            print(c)
            if (not(c[0], c[1]) in route.values()) or (not(c[1], c[0]) in route.values()):
                idx += 1
                route[idx] = ([c[0], c[1]])
    # THIS ABOVE LOOP STORES ROUTE OF EACH tuple 

    for c in stop_pairs:
        res = inPrevious(c[0], route[idx]) # if new is end of path; capacity of path is than total cap; node isn't served before
        if res == 0 and capacityValid(route[idx], c[1]) and (isServed(c[1]) == False):
            hasBeenServed(c[1])
            route[idx].append(c[1])

        elif res == 1 and capacityValid(route[idx], c[1]) and (isServed(c[1]) == False):
            hasBeenServed(c[1])
            route[idx].insert(0, c[1])

        else:
            res = inPrevious(c[1], route[idx])
            if res == 0 and capacityValid(route[idx],c[0]) and stopVisited[c[0]] == False:
                hasBeenServed(c[0])
                route[idx].insert(0, c[0])
            elif res == 1 and capacityValid(route[idx], c[0]) and stopVisited[c[1]] == False:
                route[idx].insert(0,c[0])


for point in stopPosDemand.keys():
    print(point)


for r in route.values():
    for point in r:
        print(point)

# printing each truck load
for r in route.values():
    cap = 0
    for points in r:
        cap += stopPosDemand[points]
    print(cap)

#adding depot at ends
for r in route.values():
    r.insert(0,depot)
    r.append(depot)

totalDist = 0
for k,v in route.items():
    totalDist += calculateRouteCost(v)
    print(k,"-",v)
    #print(totalDist)
print(totalDist/2)


