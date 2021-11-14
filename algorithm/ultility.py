import pandas as pd
import numpy as np
from datetime import datetime
now = str(datetime.now().timestamp())
timestamp = now.split('.')[0]

def object_function(pd_assignment):
    sum_priotity = 0
    for item in pd_assignment['Priority']:
        if item != 'n/a':
            sum_priotity += item
    return sum_priotity

def get_courses(course):
    courseDict = {}
    for i in range(len(course.index)):
        classes = float(course.iloc[i]['No. Classes'])
        if not np.isnan(classes) and classes > 0:
            CourseID = course.iloc[i][1]
            numClasses = {CourseID:classes}
            courseDict.update(numClasses)
    return courseDict

def get_neighbors(course, registration, teacher):
    list_class = registration['Course\Teacher'].tolist()
    registration = registration.drop(columns=['Unnamed: 0', 'Course\Teacher'])

    new_index = {}
    for id in range(len(registration.index.tolist())):
        new_index.update({registration.index.tolist()[id]:list_class[id]})
    registration = registration.rename(index=new_index)

    list_delete = []
    for i in range(len(course.index)):
        classes = float(course.iloc[i]['No. Classes'])
        if np.isnan(classes) or classes == 0:
            list_delete.append(registration.index.tolist()[i])
    registration = registration.drop(index=list_delete)

    list_TC_delete = []
    for i in range(len(teacher.index)):
        TC = float(teacher.iloc[i]['Max Classes'])
        if np.isnan(TC) or TC == 0:
            list_TC_delete.append(teacher['TeacherID'][i])
    registration = registration.drop(columns=list_TC_delete)

    courseDict = get_courses(course)
    for item in courseDict:
        if courseDict[item] > 1:
            registration = registration.append([registration.loc[item,:]]*int(courseDict[item] - 1))
    
    registration = registration.sort_index(ascending=True)

    listCouseID_unique = registration.index.unique().tolist()
    listCouseID = []
    for item in listCouseID_unique:
        num_class = int(courseDict[item])
        for num in range(num_class):
            nameCourseID = item + "-" + str(num + 1)
            listCouseID.append(nameCourseID)
    
    registration = registration.reset_index(drop=True)
    
    new_index = {}
    for id in range(len(registration.index.tolist())):
        new_index.update({registration.index.tolist()[id]:listCouseID[id]})
    registration = registration.rename(index=new_index)

    pd_class = registration.isna().sum(axis=1)
    priority_class = pd_class.sort_values(ascending=True).index.tolist()

    result = []
    for classID in priority_class:
        for tc in registration.columns.tolist():
            select_TC = []
            #pick TC has low priority
            # if registration.loc[classID,tc] <= registration.loc[classID,:].mean():
            #     select_TC.append(classID)
            #     select_TC.append(tc)

            #pick all TCs have priority of class
            if registration.loc[classID,tc] != 999 and not np.isnan(registration.loc[classID,tc]):
                select_TC.append(classID)
                select_TC.append(tc)
            if len(select_TC) > 0:
                result.append(select_TC)
    
    return [result,0] #[list_neigbor, position of current neighbor]

def parsePD(decision_matrix, pd_priority_matrix):
    list_classID = decision_matrix.columns.tolist()
    del list_classID[-1]

    #get teacherID, priority
    list_teacherID = []
    list_priority = []
    for classID in list_classID:
        TC = decision_matrix[decision_matrix[classID]==1].index.values.tolist()
        if len(TC) == 0:
            list_teacherID.append('n/a')
            list_priority.append('n/a')
        else:
            priority = pd_priority_matrix.loc[TC[0],classID]
            list_teacherID.append(TC[0])
            list_priority.append(priority)
    df = pd.DataFrame({'ClassID': list_classID,
                    'TeacherID': list_teacherID,
                    'Priority': list_priority})
    return df

def isValid(priority_matrix_result):
    if len(priority_matrix_result.index.tolist()) == 0:
        return False
    else:
        return True

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

def getBasicClassToBeOpen(course):
        num_class = course['Basic']*course['No. Classes']
        return num_class.sum()

def getClassToBeOpen(course):
    num_class = course['No. Classes']
    return num_class.sum()

def parseOutput(dataPath, id_method, course, solution, priority_matrix,  epochs='n/a', temp='n/a', logNumClasses='n/a', logPriority='n/a'):
    priority = object_function(parsePD(solution, priority_matrix))
    num_class = getTotalClass(solution)
    num_class_basic = getBasicClass(course, parsePD(solution, priority_matrix))
    num_class_basic_total = getBasicClassToBeOpen(course)
    num_class_open_total  = getClassToBeOpen(course)

    item_row = ['Epoch', 'Temp', 'Priority', 'Num Classes', 'Num Classes Basic', 'Method']
    num_class_basic_merge = '{:.0f}/{:.0f}'.format(num_class_basic, num_class_basic_total)
    num_class_open = '{:.0f}/{:.0f}'.format(num_class, num_class_open_total)
    value_row = [epochs, temp, priority, num_class_open, num_class_basic_merge]

    if id_method == 1:
        value_row.append('Hungarian')
    elif id_method == 2:
        value_row.append('Greedy')
    else:
        value_row.append('Greedy + Simulated Annealing')

    df_info = pd.DataFrame({'Item': item_row, 'Value': value_row})

    df_output = parsePD(solution, priority_matrix)
    df_output = df_output.sort_values(by=['ClassID'], ignore_index=True)
    with pd.ExcelWriter(dataPath + '/output_' + timestamp +'.xlsx') as writer:
        df_info.to_excel(writer, sheet_name='Result')
        df_output.to_excel(writer, sheet_name='Result', startrow=8, startcol=0)
        if id_method == 3:
            # Create a Pandas dataframe from the data.
            multi_iter1 = {'NumClass': logNumClasses, 'Priority': logPriority}
            df = pd.DataFrame(multi_iter1)
            df.to_excel(writer, sheet_name='Result', startrow=1, startcol=8)

            # Access the XlsxWriter workbook and worksheet objects from the dataframe.
            workbook  = writer.book
            worksheet = writer.sheets['Result']

            # Create a chart object.
            chart = workbook.add_chart({'type': 'line'})

            # Configure the series of the chart from the dataframe data.
            categories = ['NumClass', 'Priority']
            for i in range(len(categories)):
                col = i + 1 + 8
                chart.add_series({
                    'name':       ['Result', 1, col],
                    'categories': ['Result', 2, 8,   2 + len(logNumClasses) - 1, 8],
                    'values':     ['Result', 2, col, 2 + len(logNumClasses) - 1, col],
                })
            
            # Configure the chart axes.
            chart.set_x_axis({'name': 'Index', 'position_axis': 'on_tick'})
            chart.set_y_axis({'name': 'Value', 'major_gridlines': {'visible': False}})

            # Insert the chart into the worksheet.
            worksheet.insert_chart('G2', chart)

            # Close the Pandas Excel writer and output the Excel file.
            # writer.save()
            
    print('Solution is ready at output.xlsx')