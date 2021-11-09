import sys
import os
import numpy as np
import pandas as pd
from preprocessing import MatrixPriority
from algorithm import Hungarian, Assginments, SimulatedAnnealingAlgorithm, object_function, parsePD, get_neighbors, isValid

def parseOutput(id_method, course, solution, priority_matrix,  epochs='n/a', temp='n/a'):
    priority = object_function(parsePD(solution, priority_matrix))
    num_class = getTotalClass(solution)
    num_class_basic = getBasicClass(course, parsePD(solution, priority_matrix))
    num_class_total = getBasicClassToBeOpend(course)

    item_row = ['Epoch', 'Temp', 'Priority', 'Num Classes', 'Num Classes Basic', 'Method']
    num_class_basic_merge = '{:.0f}/{:.0f}'.format(num_class_basic, num_class_total)
    value_row = [epochs, temp, priority, num_class, num_class_basic_merge]

    if id_method == 1:
        value_row.append('Hungarian')
    elif id_method == 2:
        value_row.append('Greedy')
    else:
        value_row.append('Greedy + Simulated Annealing')

    df_info = pd.DataFrame({'Item': item_row, 'Value': value_row})

    df_output = parsePD(solution, priority_matrix)
    df_output = df_output.sort_values(by=['ClassID'], ignore_index=True)
    with pd.ExcelWriter('output.xlsx') as writer:
        df_info.to_excel(writer, sheet_name='Sheet1')
        df_output.to_excel(writer, sheet_name='Sheet1', startrow=8, startcol=0)

    print('Solution is ready at output.xlsx')

def getTotalClass(state):
    tmpValue = state.drop(columns='Max_Classes')
    return tmpValue.values.sum()

def getBasicClass(pd_course, pd_result):
    list_basic_class = []
    for clssID in pd_course.index.tolist():
        if pd_course.loc[clssID, 'Basic'] == 1:
            list_basic_class.append(pd_course.loc[clssID, 'CourseID'])

    list_class_result = []
    for clssID in pd_result.index.tolist():
        if pd_result.loc[clssID, 'Priority'] != 'n/a':
            list_class_result.append(pd_result.loc[clssID, 'ClassID'])

    cnt = 0
    for classOpen in list_class_result:
        for classBasic in list_basic_class:
            if classBasic in classOpen:
                cnt += 1
    return cnt

def getBasicClassToBeOpend(course):
        num_class = course['Basic']*course['No. Classes']
        return num_class.sum()

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
        # print('result:\n',decision_matrix_hungarian)
        return parseOutput(1, course, decision_matrix_hungarian, priority_matrix)
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
        return parseOutput(2, course, decision_matrix, priority_matrix)

    print('init neighboor list: \n',tuple_neighbors)

    #phase 2
    print('**************PHASE 2*****************')
    sa = SimulatedAnnealingAlgorithm(decision_matrix, tuple_neighbors, priority_matrix)
    solution = sa.start(500)
    sa.toString(course, solution)
    epochs, tmp = sa.getInfo()
    parseOutput(3, course, solution, priority_matrix, epochs, tmp)
    print("End!!!")

if __name__ == "__main__":
    main()