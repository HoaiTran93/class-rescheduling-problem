import numpy as np
import pandas as pd

class MatrixPriority():
    def __init__(self,course, registration, teacher):
        self.course = course.sort_values(by=['Basic'],ascending=False) #move mandantory class to left for first assginments
        self.registration = registration
        self.teacher = teacher
    
    def get_courses(self):
        self.courseDict = {}
        for i in range(len(self.course.index)):
            classes = float(self.course.iloc[i]['No. Classes'])
            if not np.isnan(classes) and classes > 0:
                CourseID = self.course.iloc[i]['CourseID']
                numClasses = {CourseID:classes}
                self.courseDict.update(numClasses)

    def get_courses_classes(self):
        self.listCouseID = []
        for item in self.courseDict.items():
            for num in range(int(item[1])):
                nameCourseID = item[0] + "-" + str(num + 1)
                self.listCouseID.append(nameCourseID)
    
    def generate(self):
        self.get_courses()
        self.get_courses_classes()
        priority_matrix = np.full((len(self.teacher.index), len(self.listCouseID)), 999)

        for id_row in range(len(self.teacher.index)):
            for id_column in range(len(self.listCouseID)):
                classid = self.listCouseID[id_column]
                classindex = int(classid[1:classid.find("-")]) - 1

                for col in range(len(self.registration.columns)):
                    if self.teacher.iloc[id_row]['TeacherID'] == self.registration.columns[col]:
                        if not np.isnan(float(self.registration.iloc[classindex][col])):
                            priority_matrix[id_row, id_column] = self.registration.iloc[classindex][col]
        pd_priority_matrix = pd.DataFrame(priority_matrix, index=self.teacher.TeacherID.tolist(), columns=self.listCouseID)
        return self.add_max_class(pd_priority_matrix)

    def add_max_class(self, pd_priority_matrix):
        pd_priority_matrix.insert(len(pd_priority_matrix.columns), 'Max_Classes', self.teacher['Max Classes'].tolist())
        return self.clean_matrix(pd_priority_matrix)

    def clean_matrix(self, pd_priority_matrix):
        #remove TCs have max_class = 0
        zero_classes = pd_priority_matrix.index[pd_priority_matrix['Max_Classes'] == 0].tolist()
        pd_priority_matrix = pd_priority_matrix.drop(index=zero_classes)

        #remove TCs dont register class
        listTC2Delete = []
        for idTC in range(pd_priority_matrix.shape[0]):
            sub_pdTC = pd_priority_matrix.iloc[idTC,:-1]
            if sub_pdTC.values.sum() == sub_pdTC.shape[0]*999:
                TC = pd_priority_matrix.index.tolist()[idTC]
                listTC2Delete.append(TC)
        pd_priority_matrix = pd_priority_matrix.drop(index=listTC2Delete)
        return pd_priority_matrix