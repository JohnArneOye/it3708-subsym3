'''
Created on 18. mars 2013

@author: JohnArne
'''
import math

#Contains objects and classes for the Artificial Neural Network
#four layers and arcs n stuff

class ANN:
    
    #Create an ANN using the parameters
    #The ANN is comprised of:
    # - Sensory Input Layer: 5 nodes with 2 arcs each
    # - Hidden Layer: 2 nodes with 4 arcs each
    # - Motor Layer: 2 nodes with 2 arcs each
    # - Bias node with 4 arcs
    def __init__(self, weights, biases, gains, time_constants):
        self.weights = weights
        self.biases = biases
        self.gains = gains
        self.time_constants = time_constants
        
        self.create_layers()
        self.create_arcs()
    
    #takes in an array with 1's on the sensors that should fire, and 0 for those who should not
    #propagates the signal through the Neural Network
    def execute(self, inputs):
        #Set inputs in the sensor nodes
        for i in range(len(inputs)):
            self.input_layer.nodes[i].set_external_input(inputs[i])
        
        #Iterate over the 12 first arcs, propagating signal from prenode to postnode
        #this means that we propagate all the values needed in the hidden layer
        for arc in self.arcs[:12]:
            arc.propagate()
            
        #Change states in the hidden layer neurons
        for node in self.hidden_layer.nodes:
            node.change_state()
        
        #Iterate over the next 10 arcs, propagating the signal down to the motor neurons
        for arc in self.arcs[12:22]:
            arc.propagate()
        
        #Change state in the output neurons
        for node in self.output_layer.nodes:
            node.change_state()
        
        #Get the output from the output neurons
        output1 = int(round(self.output_layer.nodes[0].output * 4.0))
        output2 = int(round(self.output_layer.nodes[1].output * 4.0))
        
        #Propagate the last of the arcs; motor neuron to motor neuron
        for arc in self.arcs[22:26]:
            arc.propagate()
            
        agent_dx = output1 - output2
        return agent_dx
            
    def create_layers(self):
        self.input_layer = Layer()
        for i in range(5):
            self.input_layer.add_node(Node(self.input_layer))
        
        self.hidden_layer = Layer()
        for i in range(2):
            self.hidden_layer.add_node(Node(self.hidden_layer, self.gains[i], self.time_constants[i]))
            self.hidden_layer.nodes[i].set_name("Hidden"+str(i))
            
        self.output_layer = Layer()
        for i in range(2):
            self.output_layer.add_node(Node(self.output_layer, self.gains[i+2], self.time_constants[i+2]))
            self.output_layer.nodes[i].set_name("Ouput"+str(i))
        
        self.bias_layer = Layer()
        self.bias_layer.add_node(Node(self.bias_layer))
        self.bias_layer.nodes[0].set_bias()
        
    def create_arcs(self):
        self.arcs = [Arc(self.input_layer.nodes[0], self.hidden_layer.nodes[0], self.weights[0]),
                     Arc(self.input_layer.nodes[0], self.hidden_layer.nodes[1], self.weights[1]),
                     Arc(self.input_layer.nodes[1], self.hidden_layer.nodes[0], self.weights[2]),
                     Arc(self.input_layer.nodes[1], self.hidden_layer.nodes[1], self.weights[3]),
                     Arc(self.input_layer.nodes[2], self.hidden_layer.nodes[0], self.weights[4]),
                     Arc(self.input_layer.nodes[2], self.hidden_layer.nodes[1], self.weights[5]),
                     Arc(self.input_layer.nodes[3], self.hidden_layer.nodes[0], self.weights[6]),
                     Arc(self.input_layer.nodes[3], self.hidden_layer.nodes[1], self.weights[7]),
                     Arc(self.input_layer.nodes[4], self.hidden_layer.nodes[0], self.weights[8]),
                     Arc(self.input_layer.nodes[4], self.hidden_layer.nodes[1], self.weights[9]),
                     Arc(self.bias_layer.nodes[0], self.hidden_layer.nodes[0], self.biases[0]),
                     Arc(self.bias_layer.nodes[0], self.hidden_layer.nodes[1], self.biases[1]),
                     Arc(self.bias_layer.nodes[0], self.output_layer.nodes[0], self.biases[2]),
                     Arc(self.bias_layer.nodes[0], self.output_layer.nodes[1], self.biases[3]),
                     Arc(self.hidden_layer.nodes[0], self.hidden_layer.nodes[0], self.weights[10]),
                     Arc(self.hidden_layer.nodes[0], self.hidden_layer.nodes[1], self.weights[11]),
                     Arc(self.hidden_layer.nodes[1], self.hidden_layer.nodes[0], self.weights[14]),
                     Arc(self.hidden_layer.nodes[1], self.hidden_layer.nodes[1], self.weights[15]),
                     Arc(self.hidden_layer.nodes[0], self.output_layer.nodes[0], self.weights[12]),
                     Arc(self.hidden_layer.nodes[0], self.output_layer.nodes[1], self.weights[13]),
                     Arc(self.hidden_layer.nodes[1], self.output_layer.nodes[0], self.weights[16]),
                     Arc(self.hidden_layer.nodes[1], self.output_layer.nodes[1], self.weights[17]),
                     Arc(self.output_layer.nodes[0], self.output_layer.nodes[0], self.weights[18]),
                     Arc(self.output_layer.nodes[0], self.output_layer.nodes[1], self.weights[19]),
                     Arc(self.output_layer.nodes[1], self.output_layer.nodes[0], self.weights[20]),
                     Arc(self.output_layer.nodes[1], self.output_layer.nodes[1], self.weights[21])]
        
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "ANN( Input%s Hidden%s Output%s Bias%s )"%(self.input_layer,self.hidden_layer,self.output_layer,self.bias_layer)
        
        
class Layer:
    
    def __init__(self):
        self.nodes = []
        
    def add_node(self, node):
        self.nodes.append(node)
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        s = "( "
        for n in self.nodes:
            s += str(n)
            s += " "
        s += ")"
        return s
    
    
class Node:
    
    def __init__(self, layer, gain=0.0, t=0.0):
        self.layer = layer
        self.y = 0.0
        self.inputs = []
        self.output = 0.0
        self.external_input = 0.0
        self.gain = gain
        self.t = t
        self.bias = 0.0
        self.name = ""
        self.dy = 0
        self.s = 0
        
        
    #Take all the inputs given from upstream neighbours, integrate them
    #Calculate the state derivative, and add it to get new state value.
    #Calculate the new output value from this neuron and set it to output.
    def change_state(self):
        #Integrate inputs, add external and bias
#        self.print_node_stats(self.dy, self.s)
        self.s = sum(self.inputs)
        self.inputs = []
        #Calculate state derivative
        self.dy = (-self.y + self.s) / self.t
        #Calculate the output of this neuron
        o = 1.0 + math.exp(-self.gain*self.y)
        self.output = 1.0/o 
        self.y += self.dy
        
        
    def print_node_stats(self, dy, s):
        print self.name," STATE ",self.y
        print self.name," dy ",dy
        print self.name," s ",s
        print self.name," out ",self.output
                
        
    def add_input(self, i):
        self.inputs.append(i)
        
    #Set output to 1 if this sensor is activated
    def set_external_input(self, i):
        self.output = i
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "Node(y=%s,gain=%s,t=%s)"%(self.y, self.gain, self.t)
        
    def get_layer(self):
        return self.layer
    
    #set output to 1 if this is a bias node
    def set_bias(self):
        self.output = 1.0
        
    def set_name(self, name):
        self.name = name

class Arc:
    
    def __init__(self, prenode, postnode, weight):
        self.prenode = prenode
        self.postnode = postnode
        self.weight = weight
        
    #Take the output from the prenode, multiply with the weight, set it to input in the postnode
    def propagate(self):
        output = self.prenode.output * self.weight
        self.postnode.add_input(output)
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "Arc(%s-%s w=%s"%(self.prenode,self.postnode,self.weight)
        