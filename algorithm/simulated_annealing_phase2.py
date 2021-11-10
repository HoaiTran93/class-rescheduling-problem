import sys
import numpy as np
import pandas as pd
from math import exp, log
from random import random, choice
from algorithm import Assginments
from .ultility import object_function, parsePD, getTotalClass, getBasicClass, getBasicClassToBeOpen

class SimulatedAnnealingAlgorithm():
    def __init__(self, currentState, neighboors, priorityMatrix, initTemp=100.0, finalTemp=0.01):
        self.currentState = currentState #decision matrix of S0
        self.neighboors = neighboors
        self.priorityMatrix = priorityMatrix
        self.temp = initTemp
        self.finalTemp = finalTemp
        self.currentPriority = 0
        self.earlyStopCounters = 0
        self.theBestSolution = currentState
        self.currentEpoch = 0
        #save info to print graph
        self.logNumClasses = []
        self.logPriority = []
        self.logNumClasses.append(getTotalClass(currentState))
        self.logPriority.append(object_function(parsePD(currentState, priorityMatrix)))
        
    def updateTemp(self, epochs):
        alpha = 1 - (log(self.temp) - log(self.finalTemp))/epochs
        self.temp *= alpha
    
    def updateCurrentNeighbor(self, nextNeighbor):
        self.neighboors[1] = self.neighboors[0].index(nextNeighbor) + 1
        if self.neighboors[1] >= len(self.neighboors[0]):
            self.neighboors[1] = 0

    def getNeighborsList(self):
        neighboorList = []
        cur_pos = self.neighboors[1]
        for index_1 in range(cur_pos, len(self.neighboors[0])):
            neighboorList.append(self.neighboors[0][index_1])
        for index_2 in range(0, cur_pos):
            neighboorList.append(self.neighboors[0][index_2])
        return neighboorList

    def lossFn(self,currentState, nextState):
        loss = 0
        if getTotalClass(nextState) < getTotalClass(currentState): # decrease class: reject with any priority
            loss += 999
        elif getTotalClass(nextState) == getTotalClass(currentState): #same class: select if lower priority
            priority_value_currentState = object_function(parsePD(currentState, self.priorityMatrix))
            priority_value_nextState = object_function(parsePD(nextState, self.priorityMatrix))
            loss = priority_value_nextState - priority_value_currentState
        else: # increase class:select with any priority
            loss -= 999
        return loss

    def getNextState(self, nextNeighbor):
        handler = Assginments(self.priorityMatrix, self.currentState)
        return handler.execute(nextNeighbor[0], nextNeighbor[1])
    
    def updateCurrentState(self, state, nextNeighbor):
        self.updateCurrentNeighbor(nextNeighbor)
        self.currentState = state

        if getTotalClass(self.theBestSolution) < getTotalClass(self.currentState):
            self.theBestSolution = self.currentState
        elif getTotalClass(self.theBestSolution) == getTotalClass(self.currentState):
            if object_function(parsePD(self.currentState, self.priorityMatrix)) < object_function(parsePD(self.theBestSolution, self.priorityMatrix)):
                self.theBestSolution = self.currentState
        self.logNumClasses.append(getTotalClass(self.currentState))
        self.logPriority.append(object_function(parsePD(self.currentState, self.priorityMatrix)))
    
    def earlyStopFn(self, temp, newPriority):
        if newPriority == self.currentPriority:
            self.earlyStopCounters += 1
            if self.earlyStopCounters == 3:
                return True
        else:
            self.earlyStopCounters = 0
            self.currentPriority = newPriority

        if temp < self.finalTemp:
            return True
        
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
        print('================================')

    def toString(self, course, state):
        print('==============Final Result==================')
        print('priority: ', object_function(parsePD(state, self.priorityMatrix)))
        print('num_class: ', getTotalClass(state))
        print('num_class basic: {:.1f}/{:.1f}'.format(getBasicClass(course, parsePD(state, self.priorityMatrix)), getBasicClassToBeOpen(course)))
        print('Class_PD:\n', parsePD(state, self.priorityMatrix))
        print('================================')

    def getInfo(self):
        return self.currentEpoch, self.temp, self.logNumClasses, self.logPriority

    def start(self, epochs):
        for i in range(epochs):
            self.currentEpoch = i
            cnt = 0
            neighborsList = self.getNeighborsList()
            for nextNeighbor in neighborsList:
                if cnt == len(neighborsList):
                    return self.theSolution()
                recentState = self.currentState
                nxtState = self.getNextState(nextNeighbor)
                loss = self.lossFn(recentState, nxtState)
                if loss <= 0:
                    self.updateCurrentState(nxtState, nextNeighbor)
                    break
                else:
                    prob = exp(-(loss/(self.temp + sys.float_info.epsilon)))
                    value_random = random()
                    if prob > value_random:
                        self.updateCurrentState(nxtState, nextNeighbor)
                        break
                    cnt += 1
            self.logFn(i, nextNeighbor, object_function(parsePD(self.currentState, self.priorityMatrix)), self.temp, getTotalClass(self.currentState))
            if self.earlyStopFn(self.temp, object_function(parsePD(self.currentState, self.priorityMatrix))):
                return self.theSolution()
            self.updateTemp(epochs)
        return self.theSolution()