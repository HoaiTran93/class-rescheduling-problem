import sys
import numpy as np
import pandas as pd
from preprocessing import MatrixPriority
from algorithm import Hungarian, Assginments, SimulatedAnnealingAlgorithm, object_function, parsePD, get_neighbors

def main():
    print("Start!!!")

    dataPath = sys.argv[1]
    couse_path = dataPath + '/Courses-50-15-174656.csv'
    teacher_path = dataPath + '/Teachers-50-15-174656.csv'
    register_path = dataPath + '/Registrations-50-15-174656.csv'

    course = pd.read_csv(couse_path)
    registration = pd.read_csv(register_path)
    teacher = pd.read_csv(teacher_path)

    classToBeOpen = course['No. Classes'].sum()

    mp = MatrixPriority(course, registration, teacher)
    priority_matrix = mp.generate()
    print(priority_matrix)
    #check if hungarian_algorithm can run
    ha = Hungarian(priority_matrix)
    if ha.hungarian_check():
        print('Hungarian can run with this case!!!')
        decision_matrix_hungarian = ha.generate_decision_matrix()
        print('result:\n',decision_matrix_hungarian)
        return
    else:
        print('Hangarian can not run with this case!!!')
        print('Trigger Greedy Algorithm and Simulated Annealing Algorithm')
    #phase 1
    print('**************PHASE 1*****************')
    hl = Assginments(priority_matrix)
    decision_matrix = hl.execute()
    pd_assignment = parsePD(decision_matrix, priority_matrix)
    tuple_neighbors = get_neighbors(course, registration, teacher)
    print('decision_matrix: \n',decision_matrix)
    print('pd_assignment: \n',pd_assignment)
    print('object_function:',object_function(pd_assignment))

    if hl.isBestSolution(classToBeOpen):
        print('This is a best solution for this case!!!')
        return

    print('init neighboor list: \n',tuple_neighbors)

    #phase 2
    print('**************PHASE 2*****************')
    sa = SimulatedAnnealingAlgorithm(decision_matrix, tuple_neighbors, priority_matrix)
    solution = sa.start(500)
    sa.toString(course, solution)
    print("End!!!")

if __name__ == "__main__":
    main()