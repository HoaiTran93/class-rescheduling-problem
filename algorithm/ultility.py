import pandas as pd
import numpy as np

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