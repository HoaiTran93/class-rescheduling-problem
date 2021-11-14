import sys
import os
import numpy as np
import pandas as pd
# import xlsxwriter
from preprocessing import MatrixPriority
from algorithm import Hungarian, Assginments, SimulatedAnnealingAlgorithm, object_function, parsePD, get_neighbors, isValid ,getTotalClass, getBasicClass, getBasicClassToBeOpen, parseOutput

def main():
    print("Start!!!")

    dataPath = sys.argv[1]
    list_file = os.listdir(dataPath)

    for fileID in list_file:
        if 'Course' in fileID:
            couse_path = dataPath + '/' + fileID
        if 'Teacher' in fileID:
            teacher_path = dataPath + '/' + fileID
        if 'Registration' in fileID:
            register_path = dataPath + '/' + fileID

    course = pd.read_csv(couse_path)
    registration = pd.read_csv(register_path)
    teacher = pd.read_csv(teacher_path)

    classToBeOpen = course['No. Classes'].sum()

    mp = MatrixPriority(course, registration, teacher)
    priority_matrix = mp.generate()
    print(priority_matrix)

    if not isValid(priority_matrix):
        print("Priority matrix is not valid!!!")
        return False
    
    #check if hungarian_algorithm can run
    ha = Hungarian(priority_matrix)
    if ha.hungarian_check():
        print('Hungarian can run with this case!!!')
        decision_matrix_hungarian = ha.generate_decision_matrix()
        return parseOutput(dataPath, 1, course, decision_matrix_hungarian, priority_matrix)
    else:
        print('Hangarian can not run with this case!!!')
        print('Triggered Greedy Algorithm and Simulated Annealing Algorithm')
    #phase 1
    print('**************PHASE 1*****************')
    hl = Assginments(priority_matrix)
    decision_matrix = hl.execute()
    pd_assignment = parsePD(decision_matrix, priority_matrix)
    tuple_neighbors = get_neighbors(course, registration, teacher)

    if hl.isBestSolution(classToBeOpen):
        print('Greedy algorithm can get the best solution')
        return parseOutput(dataPath, 2, course, decision_matrix, priority_matrix)
    else:
        print('Triggered Simulated Annealing Algorithm')
        print(pd_assignment)

    #phase 2
    print('**************PHASE 2*****************')
    sa = SimulatedAnnealingAlgorithm(decision_matrix, tuple_neighbors, priority_matrix)
    solution = sa.start(500)
    sa.toString(course, solution)
    epochs, tmp, logNumClasses, logPriority = sa.getInfo()
    parseOutput(dataPath, 3, course, solution, priority_matrix, epochs, tmp, logNumClasses, logPriority)

    print("End!!!")

if __name__ == "__main__":
    main()