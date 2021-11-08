import sys
import numpy as np
import pandas as pd
from preprocessing import MatrixPriority
from algorithm import Hungarian, Assginments, SimulatedAnnealingAlgorithm, object_function, parsePD, get_neighbors

def main():
    print("Start!!!")

    dataPath = sys.argv[1]
    couse_path = dataPath + '/Courses-30-30-174418.csv'
    teacher_path = dataPath + '/Teachers-30-30-174418.csv'
    register_path = dataPath + '/Registrations-30-30-174418.csv'

    course = pd.read_csv(couse_path)
    registration = pd.read_csv(register_path)
    teacher = pd.read_csv(teacher_path)

    mp = MatrixPriority(course, registration, teacher)
    priority_matrix = mp.generate()
    print(priority_matrix)

    #phase 1
    print('**************PHASE 1*****************')
    hl = Assginments(priority_matrix)
    decision_matrix = hl.execute()
    pd_assignment = parsePD(decision_matrix, priority_matrix)
    tuple_neighbors = get_neighbors(course, registration, teacher)
    print('decision_matrix: \n',decision_matrix)
    print('pd_assignment: \n',pd_assignment)
    print('object_function:',object_function(pd_assignment))
    print('init neighboor list: \n',tuple_neighbors)

    #phase 2
    print('**************PHASE 2*****************')
    sa = SimulatedAnnealingAlgorithm(decision_matrix, tuple_neighbors, priority_matrix)
    sa.start(500)
    print("End!!!")

if __name__ == "__main__":
    main()