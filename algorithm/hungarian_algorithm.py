import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment

class Hungarian():
    def __init__(self, pd_priority_matrix):
        self.pd_priority_matrix = pd_priority_matrix

    def generate_decision_matrix(self):
        matrix_tmp = np.array(self.pd_priority_matrix.drop(columns='Max_Classes'))
        row_result, col_result = linear_sum_assignment(matrix_tmp)

        row = self.pd_priority_matrix.index.tolist()
        column = self.pd_priority_matrix.columns.tolist()

        content_matrix = np.zeros(self.pd_priority_matrix.shape)
        content_matrix[row_result, col_result] = 1
        
        decision_matrix = pd.DataFrame(content_matrix, index=row, columns=column)
        decision_matrix.update(self.pd_priority_matrix['Max_Classes'])
        return decision_matrix

    def hungarian_check(self):
        for rowID in self.pd_priority_matrix['Max_Classes'].index.tolist():
            if self.pd_priority_matrix.loc[rowID, 'Max_Classes'] != 1:
                return False
        
        for rowID in self.pd_priority_matrix.index.tolist():
            for colID in self.pd_priority_matrix.columns.tolist():
                if self.pd_priority_matrix.loc[rowID, colID] == 999:
                    return False
        return True