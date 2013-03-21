'''
Created on 18. mars 2013

@author: JohnArne
'''
import random
from ANN import ANN
from tracker import Tracker

#NB! : Does not extend the Individual, must change that before implementing in EA
class Beer():
    nr_of_bits = 272
    
    def __init__(self, genotype=None):
        if genotype is None:
            self.random_genotype()
        else:
            self.genotype = genotype
        self.phenotype = []
        self.fitness = 0.0
        
    def random_genotype(self):
        self.genotype = random.getrandbits(272)
        
    def development(self):
        #Convert genotype to a string list
        gtype = int(self.genotype)
        genome_list = []
        for _ in range(0, self.nr_of_bits):
            genome_list.insert(0, str(gtype % 2))
            gtype = gtype/2
        
        #Develop 22 weights on arcs [-5.0, +5.0]
        self.arc_weights = []
        for i in range(0,176,8):
            self.arc_weights.append(dev_parameter(genome_list, i, i+8, 256, 10)-5.0)
        #Develop 4 bias-weights on arcs eminating from bias node [-10.0, 0.0]
        self.biases = []
        for i in range(176,208,8):
            self.biases.append(dev_parameter(genome_list, i, i+8, 256, 10)-10.0)
        #Develop gains for 4 neurons(2 in hidden layer and 2 in motor layer) [1.0, 5.0]
        self.gains = []
        for i in range(208,240,8):
            self.gains.append(dev_parameter(genome_list, i, i+8, 256, 4)+1.0)
        #Develop time constants for the same 4 neurons
        self.time_constants = []
        for i in range(240,272,8):
            self.time_constants.append(dev_parameter(genome_list, i, i+8, 256, 1)+1.0)
        
        #Create a new ANN with the parameters
        self.ann = ANN(self.arc_weights, self.biases, self.gains, self.time_constants)
    
    #Perform mutation on the genotype
    def mutate(self, mutation_prob, mutation_count):
        for _ in range(mutation_count):
            if random.random() < mutation_prob:
                self.genotype = self.genotype ^ (1 << random.randint(0, self.nr_of_bits))

        #Perform crossover on the genotype
    def crossover(self, other, crossover_rate):
        if random.random()<crossover_rate:
            crossover_range = (10, 150)
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
            
            return Beer(int("".join(new_genotype), 2))
        else:
            return Beer(self.genotype)
        
    def num_to_bitstring(self, n, l=20):
        return bin(n)[2:].zfill(l)
    
    def __str__(self):
        s = "Beer("
        for w in self.arc_weights:
            s+="w"
            s+=str(w)
        for b in self.biases:
            s+="b"
            s+=str(b)
        for g in self.gains:
            s+="g"
            s+=str(g)
        for t in self.time_constants:
            s+="t"
            s+=str(t)
        s+=")"
        return s
        
    def __repr__(self):
        return self.__str__()
        
#Develop a single parameter, from the binary list representing it to a float.    
def dev_parameter(glist, start, stop, binlim, lim):
    return ((int( "".join(glist[start:stop]), 2 )*1.0/binlim)*lim)  

if __name__ == '__main__':
    beer = Beer()
    beer.development()
    print beer
    print beer.ann
    print beer.ann.arcs
    tracker = Tracker(beer.ann)
    tracker.run()
    