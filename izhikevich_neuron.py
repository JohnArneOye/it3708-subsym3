from Individual import Individual
import random
import data_loader

class Izzy(Individual):
    
    nr_of_bits = 66
    t = 10.0
    I = 10.0

    threshold = 35
    
    def __init__(self, genotype=None):
        if genotype is None:
            self.initial_genotype()
        else:
            self.genotype = genotype
        self.phenotype = []
        self.fitness = 0.0
        self.v = -60.0
        self.u = 0.0
        self.distance = 0
    
    #Creates an intitial random genotype for representing the 
    #five variables; a, b, c, d, and K
    def initial_genotype(self):
        self.genotype = random.getrandbits(66)
        
    #Perform mutation on the genotype
    def mutate(self, mutation_prob, mutation_count):
        for _ in range(mutation_count):
            if random.random() < mutation_prob:
                self.genotype = self.genotype ^ (1 << random.randint(0, self.nr_of_bits))
        
    #Develop the genotype to a set of parameters, which are the phenotype for the neuron
    def development(self):
        #Convert genotype to a string list
        gtype = int(self.genotype)
        genome_list = []
        for _ in range(0, self.nr_of_bits):
            genome_list.insert(0, str(gtype % 2))
            gtype = gtype/2
        
        #Develop 'a' parameter: | RANGE: [0.001, 0.2]  *1000 -> [1, 200]
        self.a = (dev_parameter(genome_list, 0, 16, 65536, 200)+1) / 1000.0
        #Develop 'b' parameter: | RANGE: [0.01, 0.3]  *100  -> [1, 30]
        self.b = (dev_parameter(genome_list, 16, 26, 1024, 30)+1) / 100.0
        #Develop 'c' parameter: | RANGE: [-80, -30]  -30  -> [-50, 0]
        self.c = -dev_parameter(genome_list, 26, 38, 4096, 50) - 30.0
        #Develop 'd' parameter: | RANGE: [0.1, 10]  *10  -> [1, 100]
        self.d = (dev_parameter(genome_list, 38, 52, 16384, 100)+1) / 10.0
        #Develop 'k' parameter: | RANGE: [0.01, 1]  *100  -> [1. 100]
        self.k = (dev_parameter(genome_list, 52, 66, 16384, 100)+1) / 100.0
        
        #GET ON DA SPIKE TRAIN! CHOO CHOO!
        self.spiketrain = []
        for _ in range(1001):
            self.v += (1/self.t)*(self.k*self.v**2 + 5*self.v + 140 + self.I - self.u)
            self.u += (self.a/self.t)*(self.b*self.v - self.u)
            self.spiketrain.append(self.v)
        
            if self.v > self.threshold:
                self.v = self.c
                self.u += self.d
            
            
        #We must find the spikes! I.e. find where the train tops or goes over threshold?
        self.spikes = find_spikes(self.spiketrain, 0)
        
    def set_distance(self, dist):
        self.distance = dist
    
    #Perform crossover on the genotype
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
            
            return Izzy(int("".join(new_genotype), 2))
        else:
            return Izzy(self.genotype)
    
    def num_to_bitstring(self, n, l=20):
        return bin(n)[2:].zfill(l)
    
    def __str__(self):
        return "IzzyPhenotype-a%sb%sc%sd%sk%s"%(self.a,self.b,self.c,self.d,self.k)
    
    def __repr__(self):
        return self.__str__()
    
#Develop a single paramter, from the binary list representing it to a float.    
def dev_parameter(glist, start, stop, binlim, lim):
    return round( ((int( "".join(glist[start:stop]), 2 )*1.0/binlim)*lim) ) 
    
#Takes in the spiketrain, returns the data points of the spikes, i thinks        
def find_spikes(data, t):
    spikes = []
    k = 5
    l = len(data)
    for i,j in zip(range(0,l-k),range(k,l)):
        if data[i+2]==max(data[i:j]) and data[i+2]>t:
            spikes.append(i+2)  
    return spikes
    
        
