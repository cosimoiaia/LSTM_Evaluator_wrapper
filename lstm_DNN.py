#!/usr/bin/env python

##########################################
#
# lstm.py: Simple parametized python script to train e use an lstm network with tflearn for sequence evaluation.
#          Based on tflearn example code https://github.com/tflearn/tflearn/blob/master/examples/nlp/
#
# Author: Cosimo Iaia <cosimo.iaia@gmail.com>
# Date: 11/11/2016
#
# This file is distribuited under the terms of GNU General Public
#
#########################################

from __future__ import absolute_import, division, print_function

import os
import tflearn
import argparse
from tflearn.data_utils import *



FLAGS = None

def find_maxlenght(path):
    fd = open(path)
    longest = 0
    for line in fd.readlines():
        longest = max(longest, len(line))
    
    return longest


def save_model(model):
    model.save(FLAGS.model_file)

def load_model(model):
    model.load(FLAGS.model_file)


def main():

    path = FLAGS.dataset

    train = True
    if os.path.exists(FLAGS.model_file):
        train = False


    # We avoid using fixed padding and simply calculate the max lenght of our input set.
    if FLAGS.max_sequence_lenght < 1:
        maxlen = find_maxlenght(path)
    else:
        maxlen = FLAGS.max_sequence_lenght
    
    print("MaxLen = ", maxlen)
    X, Y, char_idx = textfile_to_semi_redundant_sequences(path, seq_maxlen=maxlen, redun_step=3)


    # Here we define our network structure, using common used values for node dimensions and dropout

    # Input Layer
    g = tflearn.input_data(shape=[None, maxlen, len(char_idx)])

    # Create our hidden LSTM Layers from parameters
    for i in range(FLAGS.hidden_layer_size):
        g = tflearn.lstm(g, 128, return_seq=True)
        g = tflearn.dropout(g, 0.5)

    
    # Finally our last lstm layer and a fully_connected with softmax activation for the output
    g = tflearn.lstm(g, 128)
    g = tflearn.dropout(g, 0.5)
    g = tflearn.fully_connected(g, len(char_idx), activation='softmax')

    # Let's not forget the regression
    g = tflearn.regression(g, optimizer='adam', loss='categorical_crossentropy',
                           learning_rate=0.001)
   
    # wrap it up in a DNN Model that will give us an Evaluation on the input 
    m = tflearn.DNN(g, tensorboard_verbose=0)

    # Let's train it
    if train:
        print("Training model...")
        m.fit(X, Y, validation_set=0.1, batch_size=FLAGS.batch_size, n_epoch=FLAGS.epochs, run_id=os.path.basename(path))

        # save our results
        print("Saving trained model to file ", FLAGS.model_file)
        save_model(m)
    else:
        print("Loading model from file ", FLAGS.model_file)
        load_model(m)

    # Predict a test
    #evaluate(m,char_idx,'Remeber Remember the Fifth of November')

    # Interactive Session:
    try:
        import readline
        while True:
            temp= str ( raw_input('Insert sequence to Evaluate >'))
            evaluate(m,char_idx,temp)
    except EOFError:
        print("Bye!")
        return



# Predict on give input
def evaluate(model,char_idx, string):


    # Put our string into semiredundant sequences according to our Tensor 'InputData/X:0' shape.
    sequences = []
    next_chars = []
    for i in range(0, len(string) - FLAGS.max_sequence_lenght, 3):
        sequences.append(string[i: i + FLAGS.max_sequence_lenght])
        next_chars.append(string[i + FLAGS.max_sequence_lenght])

    X = np.zeros((len(sequences), FLAGS.max_sequence_lenght, len(char_idx)), dtype=np.bool)
    Y = np.zeros((len(sequences), len(char_idx)), dtype=np.bool)
    for i, seq in enumerate(sequences):
        for t, char in enumerate(seq):
            X[i, t, char_idx[char]] = 1
        Y[i, char_idx[next_chars[i]]] = 1

    # Then simply evaluate to our model
    print("Evaluation: ", model.evaluate(X,Y))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple parametized lstm network for sequence evaluation')
    parser.add_argument('--dataset', type=str, required=True, default='', help='Path to the dataset file')
    parser.add_argument('--batch_size', type=int, default='128', help='How many string train on at a time')
    parser.add_argument('--epochs', type=int, default='1', help='How many epochs to train')
    parser.add_argument('--model_file', type=str, default='model.tfl', help='Path to save the model file, will be loaded if present or created')
    parser.add_argument('--hidden_layer_size', type=int, default=1, help='Number of hidden lstm layers')
    parser.add_argument('--lstm_node_size', type=int, default=256, help='Number of nodes in each lstm layers')
    parser.add_argument('--max_sequence_lenght', type=int, default=0, help='Max lenght of sequence sample. if 0 is set to the maximum sequence lenght from dataset (Warning: requires serious amount of Memory)')
    FLAGS = parser.parse_args()
    main()
