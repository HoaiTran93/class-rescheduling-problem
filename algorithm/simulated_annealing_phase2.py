import sys
import numpy as np
import pandas as pd
from math import exp, log
from random import random, choice
from algorithm import Assginments
from .ultility import object_function, parsePD

class SimulatedAnnealingAlgorithm():
    def __init__(self, currentState, neighboors, priorityMatrix, initTemp=100.0, finalTemp=1.0):
        self.currentState = currentState #decision matrix of S0
        self.neighboors = neighboors
        self.priorityMatrix = priorityMatrix
        self.temp = initTemp
        self.finalTemp = finalTemp
        self.tempMin = 1
        self.currentPriority = 0
        self.earlyStopCounters = 0
        self.theBestSolution = currentState
        
    
    def updateTemp(self, epochs):
        # print('updateTemp')
        # print('log(self.temp):',log(self.temp))
        # print('epochs: ',epochs)
        # print('log(self.finalTemp)', log(self.finalTemp))
        alpha = 1 - (log(self.temp) - log(self.finalTemp))/epochs
        self.temp *= alpha
        # print('alpha: ',alpha)
        # print('temp:', self.temp)
    
    def updateCurrentNeighbor(self, nextNeighbor):
        self.neighboors[1] = self.neighboors[0].index(nextNeighbor) + 1
        if self.neighboors[1] >= len(self.neighboors[0]):
            self.neighboors[1] = 0

    def getNeighborsList(self):
        neighboorList = []
        cur_pos = self.neighboors[1]
        for index_1 in range(cur_pos, len(self.neighboors[0])):
            neighboorList.append(self.neighboors[0][index_1])
        # print('cur_pos:',cur_pos)
        # print('self.neighboors[0]:',self.neighboors[0])
        for index_2 in range(0, cur_pos):
            # print('index_2:',index_2)
            neighboorList.append(self.neighboors[0][index_2])
        return neighboorList

    def getTotalClass(self, state):
        tmpValue = state.drop(columns='Max_Classes')
        return tmpValue.values.sum()
    
    # def getBasicClass(self, state):
    #     tmpValue = state.drop(columns='Max_Classes')
    #     return tmpValue.loc[tmpValue['a'] == 1, 'b'].sum()

    # def lossFn(self,currentState, nextState):
    #     print('lossFn called')
    #     priority_value_currentState = object_function(parsePD(currentState, self.priorityMatrix))
    #     priority_value_nextState = object_function(parsePD(nextState, self.priorityMatrix))

    #     print('priority_value_currentState:\n', parsePD(currentState, self.priorityMatrix))
    #     print('priority_value_nextState:\n', parsePD(nextState, self.priorityMatrix))

    #     loss = priority_value_nextState - priority_value_currentState
    #     if self.getTotalClass(nextState) < self.getTotalClass(currentState): # decrease class to decrease priority
    #         print('detect decrease num class!!!!')
    #         loss += 999
    #     return loss

    def lossFn(self,currentState, nextState):
        # print('lossFn called')
        loss = 0
        if self.getTotalClass(nextState) < self.getTotalClass(currentState): # decrease class: reject with any priority
            # print('detect decrease num class!!!!')
            loss += 999
        elif self.getTotalClass(nextState) == self.getTotalClass(currentState): #same class: select if lower priority
            # print('detect same num class!!!!')
            priority_value_currentState = object_function(parsePD(currentState, self.priorityMatrix))
            priority_value_nextState = object_function(parsePD(nextState, self.priorityMatrix))

            # print('priority_value_currentState:\n', parsePD(currentState, self.priorityMatrix))
            # print('priority_value_nextState:\n', parsePD(nextState, self.priorityMatrix))

            loss = priority_value_nextState - priority_value_currentState
        else: # increase class:select with any priority
            # print('detect increase num class!!!!')
            loss -= 999
        return loss

    def getNextState(self, nextNeighbor):
        handler = Assginments(self.priorityMatrix, self.currentState)
        return handler.execute(nextNeighbor[0], nextNeighbor[1])
    
    def updateCurrentState(self, state, nextNeighbor):
        # print('updateCurrentState')
        self.updateCurrentNeighbor(nextNeighbor)
        self.currentState = state

        if self.getTotalClass(self.theBestSolution) < self.getTotalClass(self.currentState):
            self.theBestSolution = self.currentState
        elif self.getTotalClass(self.theBestSolution) == self.getTotalClass(self.currentState):
            if object_function(parsePD(self.currentState, self.priorityMatrix)) < object_function(parsePD(self.theBestSolution, self.priorityMatrix)):
                self.theBestSolution = self.currentState
        # print('currentState:\n', self.currentState)
        # print('currentState_PD:\n', parsePD(self.currentState, self.priorityMatrix))
    
    def earlyStopFn(self, temp, newPriority):
        # print('earlyStopFn check')

        if newPriority == self.currentPriority:
            self.earlyStopCounters += 1
            # print('earlyStopCounters += 1')
            if self.earlyStopCounters == 3:
                # print('reach 3 times of same priority')
                return True
        else:
            # print('update self.currentPriority')
            self.earlyStopCounters = 0
            self.currentPriority = newPriority

        if temp < self.tempMin:
            # print('temp < self.tempMin')
            return True
        
        # print('no earlyStopFn match!!')
        return False

    def theSolution(self):
        if object_function(parsePD(self.currentState, self.priorityMatrix)) > object_function(parsePD(self.theBestSolution, self.priorityMatrix)):
            return self.theBestSolution
        else:
            return self.currentState
 
    def logFn(self, epoch, neighboor, priority, temp, num_class):
        print('==============logFn==================')
        print('epoch: ', epoch)
        print('neighboor: ', neighboor)
        print('priority: ', priority)
        print('num_class: ',num_class)
        print('temp: ', temp)
        # print('decision matrix:\n', self.currentState)
        print('Class_PD:\n', parsePD(self.currentState, self.priorityMatrix))
        print('================================')

    def toString(self, state):
        print('==============Final Result==================')
        print('priority: ', object_function(parsePD(state, self.priorityMatrix)))
        print('num_class: ',self.getTotalClass(state))
        print('Class_PD:\n', parsePD(state, self.priorityMatrix))
        print('================================')

    def start(self, epochs):
        for i in range(epochs):
            # print('===for epoch i: {0}==='.format(i))
            # print('temp run: ', self.temp)
            cnt = 0
            neighborsList = self.getNeighborsList()
            # neighborsList = neighborsList[:-1] #remove itself
            for nextNeighbor in neighborsList:
                if cnt == len(neighborsList):
                    print('No candidate in all of neighbors!!!!')
                    return self.theSolution()
                # print('neighboor list: \n', neighborsList)
                # print('nextNeighbor:', nextNeighbor)
                recentState = self.currentState
                # print('recentState:\n',recentState)
                nxtState = self.getNextState(nextNeighbor)
                # print('nxtState:\n',nxtState)
                loss = self.lossFn(recentState, nxtState)
                # print('loss:{:.10f}'.format(loss))
                if loss <= 0:
                    # print('loss <= 0')
                    self.updateCurrentState(nxtState, nextNeighbor)
                    break
                else:
                    # print('loss > 0')
                    prob = exp(-(loss/(self.temp + sys.float_info.epsilon)))
                    # print('prob:',prob)
                    value_random = random()
                    # print('value_random:',value_random)
                    if prob > value_random:
                        # print('prob > random')
                        self.updateCurrentState(nxtState, nextNeighbor)
                        break
                    cnt += 1
            
            self.logFn(i, nextNeighbor, object_function(parsePD(self.currentState, self.priorityMatrix)), self.temp, self.getTotalClass(self.currentState))

            if self.earlyStopFn(self.temp, object_function(parsePD(self.currentState, self.priorityMatrix))):
                return self.theSolution()
            
            self.updateTemp(epochs)
            # print('==endfor==')
        return self.theSolution()