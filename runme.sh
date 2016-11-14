#!/bin/bash

./lstm_DNN.py --dataset ringtones_128_trim.txt  --hidden_layer_size 1 --lstm_node_size LSTM_NODE_SIZE 128 --max_sequence_lenght 32 --batch_size 32
