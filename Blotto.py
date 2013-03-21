from abc import*
from Individual import*

class Blotto(Individual):
    
    B = 20 #The number of battles to be fought
    S = 50 #The total number of troops at disposal
    L = 1.0 #The loss factor of the strength factor, decrement when a battle is lost
    R = 0.1 #The re-deployment factor, factor of troops allowed to redeploy after winning a battle
    
    
    def __init__(self, genotype=None):
        self.phenotype = []
        self.strength_factor = 1.0 #Strength factor to be multiplied with troop
        self.fitness = 0
        if genotype is None:
            self.random_genotype()
        else:
            self.genotype = genotype
        
        
    #Increment or decrement a random list element in genotype
    @abstractmethod
    def mutate(self, mutation_prob, mutation_count):
        index = random.randint(0,self.B-1)
        probability = random.random()
        if probability<mutation_prob/2:
            if self.genotype[index] is 0: 
                self.genotype[index]+=1
            else: 
                self.genotype[index]-=1
        elif probability<mutation_prob:
            if self.genotype[index] is 10:
                self.genotype[index]-=1
            else:
                self.genotype[index]+=1
        
    @abstractmethod
    def crossover(self, other, crossover_rate):
        if random.random()<crossover_rate:
            crossover_range = ( random.randint(0,len(self.genotype)-1), random.randint(0,len(self.genotype)-1) )
            c_min = min(crossover_range)
            c_max = max(crossover_range)
            if not c_max==c_min:
                new_genotype = []
                crossover_genes = [other.genotype[i] for i in range(c_min,c_max)]
                if not c_min==0:
                    new_genotype = [self.genotype[i] for i in range(0,c_min)]
                new_genotype.extend(crossover_genes)
                if not c_max==(len(self.genotype)):
                    new_genotype.extend(self.genotype[c_max:])
                return Blotto(new_genotype)
        return Blotto(self.genotype)

        
    #Convert the 0-10 weights to resources, i.e. normalize then multiply by S
    @abstractmethod
    def development(self):
        genotype_sum = sum(self.genotype)
        if not genotype_sum==0:
            self.phenotype = [(i*1.0/genotype_sum)*self.S for i in self.genotype]
        else:
            self.phenotype = [0 for _ in self.genotype]
       
    #The initial genotype is a list of B random weights from 0 to 10 
    def random_genotype(self):
        self.genotype = [random.randint(0,10) for _ in range(0,self.B)]
        
    def increment_fitness(self, inc):
        self.fitness += inc
        
    def decrement_strength(self):
        self.strength_factor -= self.L
        
    def re_deploy(self, battle_nr, troop):
        troop_per_battle = ( troop/(len(self.phenotype)-battle_nr) )*self.R
        for i in range(battle_nr+1, len(self.phenotype)-1):
            self.phenotype[i] += troop_per_battle
    
    def reset_fitness(self):
        self.fitness = 0
                
    def reset(self):
        self.strength_factor = 1.0 
        self.development()
        
    def get_strength(self):
        return self.strength_factor
    
if __name__ == '__main__':
    population = []
    for i in range(0, 5):
        blotto = Blotto()
        blotto.development()
        population.append(blotto)
    print population
        
    FitnessEval.blotto_fitness(population)

    