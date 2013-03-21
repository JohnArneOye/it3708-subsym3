import random
import FitnessEval
import sys
from abc import*

class Individual:
    n_fitness_settings = 0
    fitness = 0
    
    @abstractmethod
    def mutate(self, mutation_prob): pass
    
    @abstractmethod
    def crossover(self, other): pass
    
    @abstractmethod
    def development(self): pass
    
    def set_fitness(self, fitness):
        """Add a fitness to average."""
        # self.n_fitness_settings += 1
        self.fitness += fitness # * (self.n_fitness_settings - 1)) + self.fitness) / self.n_fitness_settings
        # print "Added fitness:", fitness, "now we have:", self.fitness

    def __str__(self):
        return str(self.phenotype)
        
    def __repr__(self):
        return self.__str__()
    
#A Individual in the population
class OneMaxIndividual(Individual):

    nr_of_bits = 40
    
    def __init__(self, genotype=None):
        self.fitness = 0
        self.phenotype = []
        if genotype is None:
            self.random_genotype()
        else:
            self.genotype=genotype
            
    
    def random_genotype(self):
        self.genotype = random.getrandbits(self.nr_of_bits)
                 
    #Mutate the genotypes, with a probability of mutation_prob  
    def mutate(self, mutation_prob, mutation_count):
        if random.random() < mutation_prob:
            self.genotype = self.genotype ^ (1 << random.randint(0, self.nr_of_bits))
        
        
    #Perform crossover on genotypes
    def crossover(self, other, crossover_rate):
        if random.random()<crossover_rate:
            crossover_range = (2, 5)
            splits = [(i % 2, random.randint(*crossover_range)) for i in range(self.nr_of_bits / crossover_range[0])]
            
            genotypes = (self.num_to_bitstring(self.genotype), self.num_to_bitstring(other.genotype))
            
            new_genotype = []
            index = 0
            for individual, n_genes in splits:
                to_index = min(index+n_genes, self.nr_of_bits)
                new_genotype.append(genotypes[individual][index:to_index])
                
                if to_index >= self.nr_of_bits:
                    break
                
                index += n_genes
            
            return OneMaxIndividual(int("".join(new_genotype), 2))
        else:
            return OneMaxIndividual(self.genotype)

    #Develop the individual from genotype to phenotype  
    def development(self):
        gtype = int(self.genotype)
        
        for _ in range(0, self.nr_of_bits):
            self.phenotype.insert(0, gtype % 2)
            gtype = gtype/2
            
    def num_to_bitstring(self, n, l=20):
        return bin(n)[2:].zfill(l)
