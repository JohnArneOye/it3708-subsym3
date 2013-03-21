import izhikevich_neuron
#Load the training data. Returns a list of the data.

def read_training_files(data_nr=2):
    data_file = open('training_data/izzy-train'+str(data_nr)+'.dat', 'r')
    training_data = [float(x) for x in data_file.read().strip().split() if x]
    assert len(training_data) == 1001
    print "READING TRAINING FILE"
    data_file.close()
    return training_data

#if __name__ == '__main__':
#    spiketrain = read_training_files(1)
#    print spiketrain
#    print izhikevich_neuron.find_spikes(spiketrain, 0)
    
    