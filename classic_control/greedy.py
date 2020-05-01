#!/usr/bin/env python3

import router
import time
import matplotlib.pyplot as plt
import numpy as np
from time import *


def plot_stops(stops):
    plt.scatter(stops[0][0], stops[0][1], marker='o', s=150, color='xkcd:orange', edgecolor='xkcd:dark grey')
    for k, v in list(stops.items())[1:]:
        plt.scatter(v[0], v[1], marker='.', s=150, color='xkcd:pink', edgecolor='xkcd:dark grey')
        plt.text(v[0]+0.1, v[1]+0.1, str(k), fontdict=dict(color='xkcd:purple'))

def plot_students(students):
    for k, v in students.items():
        plt.scatter(v[0], v[1], marker='.', s=150, color='xkcd:sky blue', edgecolor='xkcd:dark grey')
        plt.text(v[0]+0.1, v[1]+0.1, str(k), fontdict=dict(color='xkcd:blue'))

def plot_student_potential_assignments(student_near_stops):
    for k, v in student_near_stops.items():
        stud_x, stud_y = students[k]
        for i in v:
            stop_x, stop_y = stops[i]
            plt.plot([stud_x, stop_x], [stud_y, stop_y], 'k:', lw=1.0)

def route_local_search(iterations,foutput):
    t0 = process_time()
    minvalue = float('+Inf')
    min_path_list = None
    min_students_dict = None
    foutput.write("\n--------------------INSIDE ROUTE_LOCAL_SEARCH-----------------------")
    a='\nLocal search: '+str(iterations)+' iterations'
    foutput.write(a)
    for i1 in range(iterations):
        b="\n\n`````ITERATION no: "+str(i1)+"`````"
        
        global_path_list, global_students_dict = router.route_local_search()
        c="\nintial global_path_list: "+str(global_path_list)
        d="\ninitial global_students_dict: "+str(global_students_dict)
        foutput.write(b)
        foutput.write(c)
        foutput.write(d)

        #if either is 0 go back to the previous iteration
        if global_path_list == None or global_students_dict == None:
            i1=i1-1
        
        #get the total length of the route
        dist = router.get_distance()

        #now check if this length if lesser than the min length -> make that the min length
        if dist < minvalue:
            w='\ndist:'+str(dist)
            minvalue = dist
            x="\nminvalue: "+str(minvalue)
            min_path_list = global_path_list
            y="\nmin_path_list: "+str(min_path_list)
            min_students_dict = global_students_dict
            z="\nmin_students_dict: "+str(min_students_dict)
            foutput.write(w)
            foutput.write(x)
            foutput.write(y)
            foutput.write(z)

    print('{0:.5f}s'.format(process_time()-t0))
    return [min_path_list, min_students_dict]

def init_pyplot():
    #clear all
    plt.cla()
    plt.clf()
    plt.title('{0}\nstops: {1}, students: {2}, maxwalk: {3}, capacity: {4}'.format(fn, len(stops), len(students), maxwalk, capacity))
    #black axis lines
    plt.axhline(0, color='k', lw=0.5)
    plt.axvline(0, color='k', lw=0.5)
    plt.grid(True)
    plt.xticks(np.arange(-13, 14, 1))
    plt.yticks(np.arange(-7, 14, 1))
    plt.axis([-13, 14, -7, 14])
    #plt.minorticks_on()
    plt.tight_layout()


if __name__ == '__main__':

    ############################### DRIVER FUNCTION #########################################################
    fn = 'instances/my2.txt'

    print('Router init: ', end=' ')
    t0 = process_time()
    router = router.Router(fn)
    stops = router.get_stops()
    print("----------")

    students = router.get_students()
    maxwalk = router.get_maxwalk()
    capacity = router.get_capacity()
    student_near_stops = router.get_student_near_stops()
    print('Router local search', end=' ')
    t0 = process_time()
    #setting number of iterations
    itr=10
    output_file="my2/res-"+str(itr)+"-iter.txt"
    foutput = open(output_file, "a")
    foutput.write("\t~~~~~~~~~~~~OUTPUT FOR "+ str(itr)+" ITERATIONS~~~~~~~~~~~~")
    paths, stud_assign = route_local_search(itr,foutput)
    a="\nfinally path: "+str(paths)
    b="\ntotal number of routes: "+str(len(paths))
    c="\nfinally stud_assign: "+str(stud_assign)
    foutput.write("\n--------------------FINAL OUTPUT-----------------------")
    foutput.write(a)
    foutput.write(b)
    foutput.write(c)
    print("adj:")
    print(router.adj_matrix(router.gen_adj()))
    print(router.gen_adj())
    print(router.get_distance())

    print('{0:.5f}s'.format(process_time()-t0))

    ############################### PLOTTING #########################################################
    init_pyplot()
    plot_students(students)
    plot_stops(stops)

    plt.savefig('my2-'+str(itr)+'-stops.pdf')

    plot_student_potential_assignments(student_near_stops)

    plt.savefig('my2-'+str(itr)+'0-potential-stops.pdf')

    #init again to clear potential routes
    init_pyplot()
    plot_students(students)
    plot_stops(stops)

    for k, v in stud_assign.items():
        stud_x, stud_y = students[k]
        stop_x, stop_y = stops[v]
        plt.plot([stud_x, stop_x],[stud_y, stop_y],'b-', lw=1.0)

    for path in paths:
        for i in range(len(path)+1):
            if i == 0:
                stop_x, stop_y = stops[path[0]]
                plt.plot([stops[0][0], stop_x],[stops[0][1], stop_y],'r-', lw=1.0)
            elif i == len(path):
                stop_x, stop_y = stops[path[i-1]]
                plt.plot([stops[0][0], stop_x],[stops[0][1], stop_y],'r-', lw=1.0)
            elif i < len(path):
                first_x, first_y = stops[path[i]]
                second_x, second_y = stops[path[i-1]]
                plt.plot([first_x, second_x],[first_y, second_y],'r-', lw=1.0)


    plt.savefig('my2-'+str(itr)+'-route.pdf')

