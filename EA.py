import sys
import FitnessEval
from Individual import OneMaxIndividual
from Plotting import Plotting
from Plotting import Blotting
from Plotting import NeuroPlot
from Plotting import BeerPlot
from izhikevich_neuron import Izzy
from beer_individual import Beer
import random
import Blotto

class EA:
    population_size = 80 #Size of the population
    generations = 150 #Number of generations
    generation = 0 #Current generation number
    fitness_goal = 1000 #The fitness goal - if there is one
    crossover_rate = 0.7 #The rate of which to perform crossover
    k = 5 #Group size in k_tournament
    e = 0.2 #Probability of selecting random in k_tournament
    mutation_probability = 0.6 #Probability that mutation of a specimen will occur
    mutation_count = 1 #Number of bits mutated when mutating
    rank_max = 0.0 #Max in rank selection
    rank_min = 0.0 #Min in rank selection
    overproduction_factor = 2 #The factor of children to be produced with OP
    
    stagnate_counter = 0

    population_genotype = []
    population_fitness = []
    new_generation = []
    children = []
    reproducers = []
    population = []
    
    develops = None
    adult_selection_fn = None
    parent_selection_fn = None
    fitness = None
    
    def __init__(self, individual_type, fitness_fn, adult_selection_fn, parent_selection_fn, plotting_fn):
        self.adult_selection_fn = adult_selection_fn
        self.parent_selection_fn = parent_selection_fn
        self.fitness_fn = fitness_fn
        self.plotter = plotting_fn(self)
        self.individual_type = individual_type
        self.best_individual = None
        self.best_overall_individual = None
        
    def create(self):
        for _ in range(0, self.population_size):
            self.population.append(self.individual_type())
    
    def develop(self):
        for p in self.population:
            p.development()
    
    def select(self):
        self.fitness_fn(self.population)
        
        population_fitness = [p.fitness for p in self.population]
        self.average_fitness = self.sum_population()/len(self.population)
        self.previously_best_individual = self.best_individual
        self.best_individual = self.sorted_population()[0]
        self.worst_individual = self.sorted_population()[-1]
        print "BW", self.best_individual.fitness, self.worst_individual.fitness
        self.std_deviation = sum( map(lambda x: (x - self.average_fitness)**2, population_fitness) )
        
        #keep the best overall individual
        if self.best_overall_individual is not None:
            if self.best_overall_individual.fitness < self.best_individual.fitness:
                self.best_overall_individual = self.best_individual
        else:
            self.best_overall_individual = self.best_individual
            
#        #count stagnate_counter if previously best is same fitness as this best
#        if self.previously_best_individual is not None:
#            if self.previously_best_individual.fitness == self.best_individual.fitness:
#                self.stagnate_counter += 1
#                print "STAGNATING! "+str(self.stagnate_counter)
#            else:
#                self.stagnate_counter = 0
#        #turn up mutation rate if stagnate_counter > 10
#        if self.stagnate_counter>20:
#            self.mutation_probability += 0.05
#            print "TURNING UP MUTATION RATE"
#            self.stagnate_counter = 0
            
        print "GENERATION:: " +str(self.generation)
        print "Max fitness: " +str(self.best_individual.fitness) +": " + str(self.best_individual)
        
        self.plotter.update()
        
#        if self.parent_selection_fn is Selection.rank:
#            if self.rank_max is 0:
#                self.rank_max = float( raw_input("Rank selection Max: ") )
#                self.rank_min = float( raw_input("Rank selection Min: ") )
#        if self.adult_selection_fn is Selection.over_production and self.overproduction_factor is 1:
#            self.overproduction_factor = int( raw_input("Over production factor: ") )
        self.reproducers = self.parent_selection_fn(self.population, self.sum_population(), self.overproduction_factor, self.rank_min, self.rank_max, self.k, self.e)
        print "Population", len(self.population)
        print "Reproducers", len(self.reproducers)
        
    def reproduce(self):
        self.children = []
        for p in self.reproducers:
            self.children.append(p.crossover( self.reproducers[random.randint(0,len(self.reproducers)-1)], self.crossover_rate ))
        print "Children", len(self.children)
    
    def operate(self):
        for p in self.children:
            p.mutate(self.mutation_probability, self.mutation_count)
        
    def replace(self):
        for p in self.children:
            p.development()
        self.generation += 1
        self.population = self.adult_selection_fn(self.population, self.children, self.population_size)     
    
    def sorted_population(self):
        return sorted(self.population, lambda x, y: cmp(x.fitness, y.fitness))[::-1]
    
    def sorted_children(self):
        return sorted(self.children, lambda x, y: cmp(x.fitness, y.fitness))[::-1]        

    def sum_population(self):
        fitness_sum = 0
        for p in self.population:
            fitness_sum += p.fitness
        return fitness_sum
    
#Contains the different selection protocols
#and selection mechanisms  
class Selection:
    
    #SELECTION PROTOCOLS
    @staticmethod
    def full_gen_replacement(population, children, pop_size):
        return children[:pop_size]
    
    @staticmethod
    def over_production(population, children, pop_size):
        sorted_population = sorted(children, lambda x, y: cmp(x.fitness, y.fitness))[::-1]
        return sorted_population[0:pop_size]
    
    @staticmethod
    def generational_mixing(population, children, pop_size):
        population.extend(children)
        sorted_population = sorted(population, lambda x, y: cmp(x.fitness, y.fitness))[::-1]
        return sorted_population[0:pop_size]
        
        
        

    #SELECTION MECHANISMS    
    #Fitness proportionate scaling of fitness and spins the wheel
    @staticmethod
    def fitness_proportionate(population, sum_fitness, op, rank_min, rank_max,  k=0, e=0):
        expected_mating = []
        average_fitness = sum_fitness/len(population)
        mating_wheel = []
        for p in population:
            if average_fitness == 0:
                expected_mating = 1
            else:
                expected_mating = int(round(p.fitness/average_fitness))
            for _ in range(0, expected_mating):
                mating_wheel.append(p) 
            
        #THEN SPIN ZE WHEEEEL
        reproducers = []
        for _ in range(0, int(len(population)*op) ):
            reproducers.append( mating_wheel[random.randint(0,len(mating_wheel)-1)] )
        
        
        print "Reproducers:", len(reproducers)
        return reproducers
       
    #Sigma scaling of fitness and spins the wheel 
    @staticmethod
    def sigma_scaling(population, sum_fitness, op, rank_min, rank_max, k=0, e=0):
        expected_mating = []
        population_fitness = [p.fitness for p in population]
            
        average_fitness = sum_fitness/len(population)
        standard_deviation = sum( map(lambda x: (x - average_fitness)**2, population_fitness) )
        mating_wheel = []
        for p in population:
            if standard_deviation is 0:
                expected_mating = 1
            else:
                expected_mating = int(1 + ( (p.fitness-average_fitness) / 2*standard_deviation ))
#            print "EXPECRTED MATING: "+str(expected_mating)+" FOR "+str(p)
            for _ in range(0, expected_mating):
                mating_wheel.append(p) #Indexes
        reproducers = []
        #THEN SPIN ZE WHEEEEL
        for _ in range(0, int(len(population)*op) ):
            r = random.random()
            for i in range(0,len(mating_wheel)):
                if mating_wheel[i]>r:
                    reproducers.append(population[i])
                    break
        return reproducers 
        
    #Rank scaling of fitness and spins the wheel
    @staticmethod
    def rank(population, sum_fitness, op, rank_min, rank_max, k=0, e=0):
        expected_mating = []
        sorted_population = sorted(population, lambda x, y: cmp(x.fitness, y.fitness))
        mating_wheel = []
        N = len(sorted_population)
        for i in range(N):
            rank = i+1
            expected_mating = rank_min+(rank_max-rank_min)*((rank*1.0-1)/(N*1.0-1))
            mating_wheel.append(expected_mating)
        
        mate_sum = sum(mating_wheel)
        mating_wheel[0]=mating_wheel[0]/mate_sum
        for i in range(1,len(mating_wheel)):
            mating_wheel[i]=mating_wheel[i-1]+(mating_wheel[i]/mate_sum)
        
        reproducers = []
        #THEN SPIN ZE WHEEEEL, make own method? and proper! this is crap
        for _ in range(0, int(len(population)*op) ):
            r = random.random()
            for i in range(0,len(mating_wheel)):
                if mating_wheel[i]>r:
                    reproducers.append(sorted_population[i])
                    break
        return reproducers 
    

    #Selects the index of the reproducers in the population by means of local k-tournament, currently only works on popsizes divisible by k
    @staticmethod
    def k_tournament(population, sum_fitness, op, rank_min, rank_max, k, e):
        reproducers = []
        group_k = k
        for i in range(k, len(population), k):
            #FACE-OFF!
            tournament_group = population[(i-(k)):group_k]
            for _ in range(int(len(tournament_group)*op)):
                if random.random()<e:
                    reproducers.append( tournament_group[random.randint(0, k-1)] )
                else:
                    tournament_group = sorted(tournament_group, lambda x, y: cmp(x.fitness, y.fitness))[::-1]
                    reproducers.append( tournament_group[0] )
            group_k = group_k + k
        return reproducers

FITNESS_FUNCTIONS = {1: FitnessEval.one_max_fitness,
                     2: FitnessEval.blotto_fitness,
                     3: FitnessEval.izzy_spike_interval,
                     4: FitnessEval.izzy_spike_time,
                     5: FitnessEval.izzy_waveform,
                     6: FitnessEval.aggregated_fitness,
                     7: FitnessEval.beer_fitness}

PARENT_SELECTION_FUNCTIONS = {1: Selection.fitness_proportionate, 
                              2: Selection.sigma_scaling, 
                              3: Selection.rank, 
                              4: Selection.k_tournament}

ADULT_SELECTION_FUNCTIONS = {1: Selection.full_gen_replacement, 
                             2: Selection.over_production, 
                             3: Selection.generational_mixing}

INDIVIDUAL_TYPE = {1: OneMaxIndividual,
                   2: Blotto,
                   3: Izzy,
                   4: Beer}  

PLOT_TYPE = {1: Plotting, 
             2: Blotting, 
             3: NeuroPlot, 
             4: BeerPlot}

USED_FITNESS_FUNCTIONS = (
    FitnessEval.izzy_spike_interval,
    FitnessEval.izzy_spike_time,
    FitnessEval.izzy_waveform,
    FitnessEval.spike_count_difference_penalty,
)

if __name__ == '__main__':
#    individual_type = int( raw_input("OneMax, Blotto or Izzy "))
#    parent_selection_nr = int( raw_input("Parent Selection: ") )
#    adult_selection_nr = int( raw_input("Adult selection: ") )
#    fitness_fn = int( raw_input("Fitness function: "))
    ea = EA(INDIVIDUAL_TYPE[4], FITNESS_FUNCTIONS[7], ADULT_SELECTION_FUNCTIONS[2], PARENT_SELECTION_FUNCTIONS[4], PLOT_TYPE[4])
    ea.create()
    ea.develop()
    
    for _ in range(0, ea.generations):
        ea.select()
        ea.reproduce()
        ea.operate()
        ea.replace()
    
    ea.plotter.plot()
    print "BEST OVERALL: "+str(ea.best_overall_individual.fitness)+" "+str(ea.best_overall_individual)
    #run the best individual with display?
    
#    population = [Izzy() for _ in range(1000)]
#    print [p.genotype for p in population]
#    for p in population:
#        p.development()
#    for p in population:
#        print p
#     
       
