from copy import copy
import izhikevich_neuron
import beer_individual
from data_loader import read_training_files
import math
import numpy as np
from tracker import Tracker

#Class for evaluation the fitness of a given phenotuype.

def one_max_fitness(population):
    goal_bits = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    print goal_bits
    for individual in population:
        fitness = 0
        for p,g in zip(individual.phenotype, goal_bits):
            if p==g:
                fitness += 1
        individual.set_fitness(fitness)

#Receives list of a population of blotto strategies, pits every commanders against
#each other, awards fitness points when winning war against another commander
def blotto_fitness(population):
    for p in population:
        p.reset_fitness()
    population_copy = copy(population)
    for commander in population:
        population_copy.remove(commander)
        for opposing_commander in population_copy:
            
            #Execute a WAR!
            points_commander = 0
            points_opponent = 0
            battle_nr = 0
            for i,j in zip(commander.phenotype, opposing_commander.phenotype):
                i = i*commander.get_strength()
                j = j*opposing_commander.get_strength()

                if i>j:
                    points_commander+=2
                    commander.re_deploy(battle_nr, i-j)
                    opposing_commander.decrement_strength()
                if i<j:
                    points_opponent+=2
                    opposing_commander.re_deploy(battle_nr, j-i)
                    commander.decrement_strength()
                battle_nr += 1
                
            #WAR done, increment fitness of winner based on points
            if points_commander>points_opponent:
                commander.increment_fitness(2)
            if points_commander<points_opponent:
                opposing_commander.increment_fitness(2)
            if points_commander==points_opponent:
                commander.increment_fitness(1)
                opposing_commander.increment_fitness(1)
            commander.reset()
            opposing_commander.reset()
            
#3 different fitness calculations: 
#Spike Time
#Spike Interval
#Waveform
#trainingdata = read_training_files()
trainingdata = []
def izzy_spike_time(p, training_spikes):
    power = 4
    S_b = training_spikes
    S_a = p.spikes
        
    N = min(len(S_a),len(S_b))
    if N == 0:
        return 0.0
        
    sigma = 0
    for t_ai, t_bi in zip(S_a, S_b):
        sigma += abs(t_ai - t_bi)**power
        
    nv = sigma ** (power ** -1)
    dist = nv/N
        
    # print "DISTANCE "+str(dist)
    p.set_distance( dist )
    if dist == 0:
        return 1000
    
    fitness = (1.0/dist)*200
    # print "Spike time", "Fitness", fitness
    return fitness * 10

def izzy_spike_interval(p, training_spikes):
    power = 4
    S_b = training_spikes
    S_a = p.spikes
        
    N = min(len(S_a), len(S_b))
        
    if N <= 1:
        return 0.0
        
    sigma = 0
    for i in range(1, N):
        sigma += abs((S_a[i] - S_a[i-1]) - (S_b[i] - S_b[i-1]))**power
        
    distance = sigma ** (power ** -1) / (N - 1)
    # print "DISTANCE", distance
    if distance == 0:
        return 1000
    
    fitness = (1 / distance) * 300
    # print "Spike interval", "Fitness", fitness
    return fitness / 2.0

def izzy_waveform(p, training_spikes):
    power = 2
    step = 5
    st = p.spiketrain[::step]
    td = trainingdata[::step]
        
    tsum = 0
    for va,vb in zip(st, td):
        tsum += (va-vb)**power
    tsum = tsum**(power**-1)
    tsum /= 1000 * step
    # print "Distance", tsum
    # print "Waveform", "Fitness", 1/tsum
    return 5/tsum

def spike_count_difference_penalty(p, training_spikes):
    N = max((len(training_spikes), len(p.spikes)))
    M = min((len(training_spikes), len(p.spikes)))
    
    if M == 0:
        return 0
    
    L = len(trainingdata)
    penalty = 1.0 * (N - M) * L / (2 * M)
    fitness = -penalty / 10.0
    # diff = abs(len(training_spikes) - len(p.spikes))
    # fitness = (2*len(trainingdata)) / diff
    # fitness = - 10.0 / fitness
    # print len(p.spikes) - len(training_spikes), "yields", fitness
    return fitness
    # print "DIFF", fitness
    # p.set_fitness(fitness)

def aggregated_fitness(population):
    training_spikes = izhikevich_neuron.find_spikes(trainingdata, 0)
    print "Training spikes", training_spikes
    
    for p in population:
        fitnesses = []
        for fn in (izzy_spike_time, izzy_spike_interval, izzy_waveform):
            fitnesses.append(fn(p, training_spikes=training_spikes))
            
        avg_fitness = sum(fitnesses) / len(fitnesses)
        
        p.fitness = avg_fitness

#The beer fitness function performs game simulation with each of the ANN's 
#in the population, and designates fitness values based on how many points
#each agent gets in the simulation.
def beer_fitness(population):
    for p in population:
        #perform simulation
        points = []
        for i in range(10):
#            print p.ann
            t = Tracker(p.ann)
            points.append(t.run())
        p.fitness = sum(points)*1.0/len(points)*1.0
    
if __name__ == '__main__':
    beer_fitness([])