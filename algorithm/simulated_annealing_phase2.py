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
        self.earlyStopCounters = 0
        
    
    def updateTemp(self, epochs):
        print('updateTemp')
        alpha = 1 - (log(self.temp) - log(self.finalTemp))/epochs
        self.temp *= alpha
        print('temp:', self.temp)
    
    def updateCurrentNeighbor(self):
        self.neighboors[1] += 1
        if self.neighboors[1] >= len(self.neighboors):
            self.neighboors[1] = 0

    def getNeighborsList(self):
        neighboorList = []
        cur_pos = self.neighboors[1]
        for index_1 in range(cur_pos, len(self.neighboors[0])):
            neighboorList.append(self.neighboors[0][index_1])
        print('cur_pos:',cur_pos)
        print('self.neighboors[0]:',self.neighboors[0])
        for index_2 in range(0, cur_pos):
            print('index_2:',index_2)
            neighboorList.append(self.neighboors[0][index_2])
        return neighboorList

    def getTotalClass(self, state):
        tmpValue = state.drop(columns='Max_Classes')
        return tmpValue.values.sum()

    def lossFn(self,currentState, nextState):
        print('lossFn called')
        priority_value_currentState = object_function(parsePD(currentState, self.priorityMatrix))
        priority_value_nextState = object_function(parsePD(nextState, self.priorityMatrix))

        print('priority_value_currentState:\n', parsePD(currentState, self.priorityMatrix))
        print('priority_value_nextState:\n', parsePD(nextState, self.priorityMatrix))

        loss = priority_value_nextState - priority_value_currentState
        if self.getTotalClass(nextState) < self.getTotalClass(currentState): # decrease class to decrease priority
            print('detect decrease num class!!!!')
            loss += 999
        return loss

    def getNextState(self, nextNeighbor):
        handler = Assginments(self.priorityMatrix, self.currentState)
        return handler.execute(nextNeighbor[0], nextNeighbor[1])
    
    def updateCurrentState(self, state):
        print('updateCurrentState')
        self.updateCurrentNeighbor()
        self.currentState = state
        print('currentState:\n', self.currentState)
        print('currentState_PD:\n', parsePD(self.currentState, self.priorityMatrix))
    
    def earlyStopFn(self, temp, earlyStopCounters):
        print('earlyStopFn check')
        if earlyStopCounters == 5:
            print('self.earlyStopCounters == 5')
            return True
        elif temp < self.tempMin:
            print('temp < self.tempMin')
            return True
        else:
            print('check fail')
            return False

    def logFn(self, epoch, neighboor, priority, avgLoss, temp):
        print('==============logFn==================')
        print('epoch: ', epoch)
        print('neighboor: ', neighboor)
        print('priority: ', priority)
        print('avg loss: ', avgLoss)
        print('temp: ', temp)
        print('================================')

    def start(self, epochs):
        for i in range(epochs):
            print('===for epoch===')
            print('epoch run: ', i)
            print('temp run: ', self.temp)
            totalLoss = 0.0
            cnt = 0
            self.earlyStopCounters = 0
            for nextNeighbor in self.getNeighborsList():
                print('neighboor list: \n', self.getNeighborsList())
                print('nextNeighbor:', nextNeighbor)
                recentState = self.currentState
                print('recentState:\n',recentState)
                nxtState = self.getNextState(nextNeighbor)
                print('nxtState:\n',nxtState)
                loss = self.lossFn(recentState, nxtState)
                print('loss:{:.10f}'.format(loss))
                if loss < 0:
                    print('loss < 0')
                    self.updateCurrentState(nxtState)
                    break
                else:
                    print('loss >= 0')
                    prob = exp(-(loss/(self.temp + sys.float_info.epsilon)))
                    print('prob:',prob)
                    value_random = random()
                    print('value_random:',value_random)
                    if prob >= value_random:
                        print('prob > random')
                        self.updateCurrentState(nxtState)
                        break
                    else:
                        self.earlyStopCounters += 1
                    totalLoss += loss
                    cnt += 1
            
            avgLoss = -1.0
            if cnt > 0:
                avgLoss = totalLoss / cnt
            
            self.logFn(i, nextNeighbor, object_function(parsePD(self.currentState, self.priorityMatrix)), avgLoss, self.temp)

            if self.earlyStopFn(self.temp, self.earlyStopCounters):
                return
            
            self.updateTemp(epochs)
            print('==endfor==')



        
