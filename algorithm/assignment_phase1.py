import numpy as np
import pandas as pd

class Assginments():
    def __init__(self, pd_priority_matrix, decision_matrix=None):
        self.housekeeping_list = []
        self.pd_priority_matrix = pd_priority_matrix
        if decision_matrix is None:
            self.decision_matrix = self.generate_decision_matrix(pd_priority_matrix)
        else:
            self.decision_matrix = decision_matrix.copy()

    def generate_decision_matrix(self, pd_priority_matrix):
        row = pd_priority_matrix.index.tolist()
        column = pd_priority_matrix.columns.tolist()
        content_matrix = np.zeros(pd_priority_matrix.shape)
        decision_matrix = pd.DataFrame(content_matrix, index=row, columns=column)
        decision_matrix.update(pd_priority_matrix['Max_Classes'])
        return decision_matrix

    def update_decision(self, row_name, column_name):
        id_row = self.decision_matrix.index.tolist().index(row_name)
        if sum(self.decision_matrix.iloc[id_row,:-1]) < self.decision_matrix.iloc[id_row,-1]:
            if self.pd_priority_matrix.loc[row_name, column_name] == 999:
                return False
            return True
        else:
            return False

    def assign_class(self, pd_class):
        flag_update_with_priority_TC = False
        name_class = pd_class.columns[0]
        priorityTCs = pd_class[pd_class['Max_Classes']==1].index.values.tolist()

        if len(priorityTCs) == 1: #only 1TC has max_class = 1
            if self.update_decision(priorityTCs[0], name_class):
                self.decision_matrix.loc[priorityTCs, name_class] = 1
                flag_update_with_priority_TC = True
        elif len(priorityTCs) > 1: # >= 2TCs have max_class = 1
            sub_pd_class = pd_class.loc[priorityTCs, :]
            sub_pd_class = sub_pd_class.sort_values(by=[name_class])
            for TC in sub_pd_class.index.values.tolist():
                if self.update_decision(TC, name_class):
                    self.decision_matrix.loc[TC, name_class] = 1
                    flag_update_with_priority_TC = True
                    break
        if not flag_update_with_priority_TC: # no update with priority TC
            pd_class = pd_class.sort_values(by=[name_class])
            for TC in pd_class.index.values.tolist():
                if self.update_decision(TC, name_class):
                    self.decision_matrix.loc[TC, name_class] = 1
                    break

    def housekeeping(self):
        for idTC in range(len(self.decision_matrix.index)):
            if sum(self.decision_matrix.iloc[idTC, :-1]) == self.decision_matrix.iloc[idTC, -1]:
                if idTC not in self.housekeeping_list:
                    self.pd_priority_matrix_backup = self.pd_priority_matrix_backup.drop(index=self.decision_matrix.index[idTC])
                    self.housekeeping_list.append(idTC)

    def refresh_decision_matrix(self, class_begin):
        class_list = self.decision_matrix.columns.tolist()
        del class_list[-1]
        start_index = class_list.index(class_begin)
        class_list = class_list[start_index:]

        for classID in class_list:
            for tcID in self.decision_matrix.index.tolist():
                self.decision_matrix.loc[tcID, classID] = 0
        return self.decision_matrix

    def assign_class_begin(self, class_begin, TC_begin):
        pd_class = self.pd_priority_matrix_backup[[class_begin, 'Max_Classes']]
        name_class = pd_class.columns[0]
        if self.update_decision(TC_begin, name_class):
            self.decision_matrix.loc[TC_begin, name_class] = 1
    
    def execute(self, class_begin=None, TC_begin=None):
        self.pd_priority_matrix_backup = self.pd_priority_matrix.copy()
        class_list = self.pd_priority_matrix_backup.columns.tolist()
        del class_list[-1]

        #reset housekeep list
        self.housekeeping_list = []

        if class_begin is not None and TC_begin is not None:
            self.refresh_decision_matrix(class_begin)
            self.assign_class_begin(class_begin, TC_begin)
            self.housekeeping()

            start_index = class_list.index(class_begin)
            if start_index + 1 == len(class_list):
                return self.decision_matrix
            else:
                start_index = start_index + 1
                class_list = class_list[start_index:]

        for classID in class_list:
            pd_class = self.pd_priority_matrix_backup[[classID, 'Max_Classes']]
            self.assign_class(pd_class)
            self.housekeeping()

        return self.decision_matrix

    def getTotalClass(self, decision_matrix):
        tmpValue = decision_matrix.drop(columns='Max_Classes')
        return tmpValue.values.sum()

    def isBestSolution(self, classToBeOpen):
        if self.getTotalClass(self.decision_matrix) == classToBeOpen:
            return True
        else:
            return False

