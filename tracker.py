'''
Created on 19. mars 2013

@author: JohnArne
'''
import random
import numpy as np
import copy
class Tracker:
    width = 30
    height = 15
    agent_y = 14
    save_to_file = False
    
    #run with true save_to_file parameter to save the run to a text file
    def __init__(self, ann, save_to_file=False):
        self.agent_pos = [12,13,14,15,16]
        self.agent_x = 12
        self.agent_dx = 0
        
        self.blocks = []
        self.create_blocks()
        self.active_blocks = []
        
        
        self.save_to_file = save_to_file
        self.run_string = str(ann)+"\n"
        
        self.ann = ann
        self.agent_points = 0
        
    #runs through the game for the number of blocks in block list
    def run(self):
        while( (len(self.active_blocks) is not 0) or (len(self.blocks) is not 0) ):
#            self.print_board()
            if self.save_to_file:
                self.print_board()
            self.check_sensors()
            self.give_points()
            self.timestep() 
            self.send_block()
        
        if self.save_to_file: 
            f = open("runs/run.txt", "w")
            f.write(self.run_string) 
            f.close()   
        return self.agent_points
    
    
    #Check if there is sensory activity, i.e. if a block is above one of the agents positions
    #If there is activity, send to ann, set agent_dx accordingly [-4, 4]
    def check_sensors(self):
        sensors = [0, 0, 0, 0, 0]
        for i in range(len(sensors)):
            for block in self.active_blocks:
                if block.positions.count(self.agent_pos[i]) > 0:
                    sensors[i] = 1
        self.agent_dx = self.ann.execute(sensors)
    
    #Move the agent and all blocks, if blocks are at position 14, delete them from the active list
    def timestep(self):
        
        #MOVE
        blocklist = self.active_blocks[:]
        for b in blocklist:
            if b.y is 14:
                self.active_blocks.remove(b)
            else:
                b.move()
        self.move_agent()
        
    
    #Check if the agent consumes or crashes in a block, give points accordingly
    def give_points(self):
        #Check if the lowest block is at y=14
        if len(self.active_blocks) is not 0:
            block = self.active_blocks[0]
            if block.y is 14:
                #Increment agent point if it fully consumes a block smaller than itself
                intersection = list(set(self.agent_pos) & set(block.positions))
                intersection_size = len( intersection )
#                if block.size<5 and intersection_size is block.size:
#                    self.agent_points += 10
#                #increment agent points if it has avoided a block larger than itself
#                if intersection_size==0:
#                    if block.size>4:
#                        self.agent_points += 0
#                    #decrement agent points if it avoids a block that it should've catched
#                    if block.size<5:
#                        self.agent_points -= 5
#                #decrement agent points it it is hit by a block and doesn't consume it
#                if intersection_size>0 and intersection_size<block.size:
#                    self.agent_points -= 5
                #Increment agent points if it consumes a block, regardless of size
                if intersection_size==block.size or intersection_size==len(self.agent_pos):
                    self.agent_points+=10  
#                #Decrement agent points if it doesn't catch a block
#                if intersection_size==0:
#                    self.agent_points-=5              
    
    #Send a new block into the environment
    def send_block(self):
#        if random.random()<0.25 and len(self.blocks) is not 0:
#            self.active_blocks.append(self.blocks.pop())
        if (len(self.active_blocks) is 0) and (len(self.blocks) is not 0):
            self.active_blocks.append(self.blocks.pop())
        
    #Move the agent along the x-axis according to the agent_dx, set new position array
    def move_agent(self):
        self.agent_x += self.agent_dx
        if self.agent_x>29:
            self.agent_x = 0
        if self.agent_x<0:
            self.agent_x = 29
        self.agent_pos = []
        for i in range(5):
            pos = self.agent_x+i
            if pos>29:
                pos = pos-30
            self.agent_pos.append(pos)
        
    #Create 20 random objects
    def create_blocks(self):
        for i in range(40):
            o = Block(1, 0, random.randint(1,6), random.randint(0,29))
            self.blocks.append(o)
            
    
    def print_board(self):
        #DISPLAY IN CONSOLE!
        environment = np.array([0 for _ in range(450)]).reshape(15, 30)
        current_display = copy.copy(environment)
        for block in self.active_blocks:
            for i in block.positions:
                current_display[block.y][i] = 2
        for i in self.agent_pos:
            current_display[14][i] = 1
        
        print "AGENT POINTS: "+str(self.agent_points)
        print ""
        board = "\n"
        for line in current_display:
            line_str = ""
            for i in line:
                if i == 0:
                    line_str += "|"
                if i == 1:
                    line_str += "_"
                if i == 2:
                    line_str += "#"
            print line_str
            board += line_str
            board += "\n"
        self.run_string+=board
        self.run_string+="\n"

        if not self.save_to_file:
            raw_input("--> cont")

class Block:
    
    def __init__(self, dy, dx, size, starting_pos):
        self.dx = dx
        self.dy = dy
        self.size = size
        self.x = starting_pos
        self.y = 0
        self.wrap()
    
    def move(self):
        self.x += self.dx
        if self.x>29:
            self.x = 0
        if self.x<0:
            self.x = 29
        self.y += self.dy
        self.wrap()
            
    def wrap(self):
        self.positions = []
        for i in range(self.size):
            pos = self.x+i
            if pos>29:
                pos = pos-30
            self.positions.append(pos)
        
            
            
                
#        [self.x+i for i in range(self.size)]

if __name__ == '__main__':
    tracker = Tracker(None)
    tracker.run()