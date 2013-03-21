import matplotlib.pyplot as plt
import numpy as np
import math
from tracker import Tracker
from data_loader import read_training_files

class BeerPlot:
    
    def __init__(self, ea):
        self.ea = ea
        # [[ max_fitness, avg_fitness, std_deviation ]]
        self.generation = []
        self.max_fitness = []
        self.avg_fitness = []
        self.std_deviation = []
        
    def plot(self):
        
        title_string = "Pop size: %s. Generations: %s Fitness: %s \nC-rate: %s M-rate: %s Overproduction: %s R-Max: %s K: %s"%(
                                                                      self.ea.population_size,
                                                                      self.ea.generation,
                                                                      self.ea.best_overall_individual.fitness, 
                                                                      self.ea.crossover_rate,
                                                                      self.ea.mutation_probability,
                                                                      self.ea.overproduction_factor,
                                                                      self.ea.rank_max,
                                                                      self.ea.k)
        
        run_string = "%s-%spop-%sgen-%sfit-%scross-%smut-%sop-%srmax-%sk"%("EA",
                                                                      self.ea.population_size,
                                                                      self.ea.generation,
                                                                      self.ea.best_overall_individual.fitness, 
                                                                      self.ea.crossover_rate,
                                                                      self.ea.mutation_probability,
                                                                      self.ea.overproduction_factor,
                                                                      self.ea.rank_max,
                                                                      self.ea.k)
        
        fig = plt.figure()
        plt.title(title_string)
        plt.subplot(211)
        plt.plot(self.generation, self.max_fitness, self.generation, self.avg_fitness)
        plt.ylabel("Max and average fitness")
        
        plt.subplot(212)
        plt.plot(self.generation, self.std_deviation)
        plt.ylabel("Standard deviation")
        fig.savefig("fitnessplots/"+run_string+".png")

        #Run one to save run to text file with the best individual        
        Tracker(self.ea.best_overall_individual.ann, True).run()
        #Pickle the best individual?
    
    
    def update(self):
        self.generation.append(self.ea.generation)
        self.max_fitness.append(self.ea.best_individual.fitness)
        self.avg_fitness.append(self.ea.average_fitness)
        self.std_deviation.append(self.ea.std_deviation)
    
    #Play out and vizualise the simulation of the best individual in the population
    def best_plot(self):
        pass
    

class Plotting:
    ea = None
    
    def __init__(self, ea):
        self.ea = ea
        # [[ max_fitness, avg_fitness, std_deviation ]]
        self.generation = []
        self.max_fitness = []
        self.avg_fitness = []
        self.std_deviation = []
        
    def plot(self):
        
        plt.figure(1)
        plt.subplot(211)
        plt.plot(self.generation, self.max_fitness, self.generation, self.avg_fitness)
        plt.ylabel("Max and average fitness")
        
        plt.subplot(212)
        plt.plot(self.generation, self.std_deviation)
        plt.ylabel("Standard deviation")
        plt.show()
    
    def update(self):
        self.generation.append(self.ea.generation)
        self.max_fitness.append(self.ea.best_individual.fitness)
        self.avg_fitness.append(self.ea.average_fitness)
        self.std_deviation.append(self.ea.std_deviation)

class Blotting:
    
    def __init__(self, ea):
        self.ea = ea
        self.generation = []
        self.max_fitness = []
        self.avg_fitness = []
        self.std_deviation = []
        self.avg_entropy = []
        
        
    def plot(self):
        plt.figure(1)
        plt.subplot(311)
        plt.plot(self.generation, self.max_fitness, self.generation, self.avg_fitness)
        plt.ylabel("Max and average fitness")
        
        plt.subplot(312)
        plt.plot(self.generation, self.std_deviation)
        plt.ylabel("Standard deviation")
        
        plt.subplot(313)
        plt.plot(self.generation, self.avg_entropy)
        plt.ylabel("Average entropy")
        plt.show()
    
    def update(self):
        self.generation.append(self.ea.generation)
        self.max_fitness.append(self.ea.best_individual.fitness)
        self.avg_fitness.append(self.ea.average_fitness)
        self.std_deviation.append(self.ea.std_deviation)
        entropy = []
        for individual in self.ea.population:
            individual_entropy = 0
            for i in individual.phenotype:
                if not i==0:
                    individual_entropy += ( i*math.log(i,2) )
            entropy.append( -individual_entropy)
        self.avg_entropy.append(sum(entropy)/len(entropy))

class NeuroPlot:
    
    def __init__(self, ea):
        self.ea = ea
        self.generation = []
        self.max_fitness = []
        self.avg_fitness = []
        self.std_deviation = []
    
    def update(self):
        self.generation.append(self.ea.generation)
        self.max_fitness.append(self.ea.best_individual.fitness)
        self.avg_fitness.append(self.ea.average_fitness)
        self.std_deviation.append(self.ea.std_deviation)
    
    def plot(self):
        training_nr = 1
        spiketrain1 = self.ea.best_overall_individual.spiketrain
        spiketrain2 = read_training_files()
        
        title_string = "Pop size: %s. Generations: %s Fitness: %s Distance: %s \nC-rate: %s M-rate: %s Overproduction: %s R-Max: %s Dataset: %s \n%s"%(
                                                                      self.ea.population_size,
                                                                      self.ea.generation,
                                                                      self.ea.best_overall_individual.fitness, 
                                                                      self.ea.best_overall_individual.distance, 
                                                                      self.ea.crossover_rate,
                                                                      self.ea.mutation_probability,
                                                                      self.ea.overproduction_factor,
                                                                      self.ea.rank_max,
                                                                      training_nr, 
                                                                      self.ea.best_overall_individual)
        fig = plt.figure()
        plt.title(title_string, fontsize=10)
        plt.plot(xrange(0,1001), spiketrain1, xrange(0,1001), spiketrain2)
        plt.ylabel("Test spiketrain vs best evolved spiketrain")
        run_string = "%s-%spop-%sgen-%sfit-%sdist-%scross-%smut-%sop-%srmax-%sdata-%s.png"%("EA",
                                                                      self.ea.population_size,
                                                                      self.ea.generation,
                                                                      self.ea.best_overall_individual.fitness, 
                                                                      self.ea.best_overall_individual.distance, 
                                                                      self.ea.crossover_rate,
                                                                      self.ea.mutation_probability,
                                                                      self.ea.overproduction_factor,
                                                                      self.ea.rank_max,
                                                                      training_nr, 
                                                                      self.ea.best_overall_individual)
        fig.savefig("spiketrains/"+run_string+".png")
        print run_string +" fit:" +str(self.ea.best_overall_individual.fitness)+" dist:"+str(self.ea.best_overall_individual.distance) + str(self.ea.best_overall_individual)
        
        fig = plt.figure()
        plt.title(title_string)
        plt.subplot(211)
        plt.plot(self.generation, self.max_fitness, self.generation, self.avg_fitness)
        plt.ylabel("Max and average fitness")
        
        plt.subplot(212)
        plt.plot(self.generation, self.std_deviation)
        plt.ylabel("Standard deviation")
        fig.savefig("fitnessplots/"+run_string+".png")
        
    
    #Take in a izzy neuron and plot the spike train and the spikes and stuff
    def plot_neuron(self):
        pass