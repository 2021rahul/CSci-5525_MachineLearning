#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 09:31:42 2018

@author: 2021rahul
"""

""" Starter code for logistic regression model
with MNIST in TensorFlow
MNIST dataset: yann.lecun.com/exdb/mnist/
"""
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import time

# Define paramaters for the model
learning_rate = 0.01
batch_size = 128
n_epochs = 50

# Step 1: Read in data
# using TF Learn's built in function to load MNIST data to the folder data/mnist
mnist = input_data.read_data_sets('/data/mnist', one_hot=True)

# Step 2: create placeholders for features and labels
# each image in the MNIST data is of shape 28*28 = 784
# therefore, each image is represented with a 1x784 tensor
# there are 10 classes for each image, corresponding to digits 0 - 9.
# Features are of the type float, and labels are of the type int
with tf.name_scope('data'):
    X = tf.placeholder(shape=[None, 784], dtype=tf.float32, name="inputs")
    Y = tf.placeholder(shape=[None, 10], dtype=tf.float32, name="labels")

# Step 3: create weights and bias
# weights and biases are initialized to 0
# shape of w depends on the dimension of X and Y so that Y = X * w + b
# shape of b depends on Y
with tf.name_scope("Variables"):
    with tf.name_scope("Weights"):
        weights = tf.Variable(tf.truncated_normal(shape=[784, 10], stddev=0.1))
    with tf.name_scope("Biases"):
        biases = tf.Variable(tf.constant(value=0.1, shape=[10]))

# Step 4: build model
# the model that returns the logits.
# this logits will be later passed through softmax layer
# to get the probability distribution of possible label of the image
# DO NOT DO SOFTMAX HERE
logits = tf.nn.bias_add(tf.matmul(X, weights, name="multiply_weights"), biases, name="add_bias")

# Step 5: define loss function
# use cross entropy loss of the real labels with the softmax of logits
# use the method:
# tf.nn.softmax_cross_entropy_with_logits(logits, Y)
# then use tf.reduce_mean to get the mean loss of the batch
with tf.name_scope("cost_function"):
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=Y))
tf.summary.scalar('loss', loss)

global_step = tf.Variable(0, name='global_step',trainable=False)
# Step 6: define training op
# using gradient descent to minimize loss
with tf.name_scope("train"):
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss, global_step=global_step)

merged_summary_op = tf.summary.merge_all()
with tf.Session() as sess:
    start_time = time.time()
    summary_writer = tf.summary.FileWriter("output/LogReg", sess.graph)
    sess.run(tf.global_variables_initializer())
    n_batches = int(mnist.train.num_examples / batch_size)
    for i in range(n_epochs):  # train the model n_epochs times
        total_loss = 0
        for batch in range(n_batches):
            X_batch, Y_batch = mnist.train.next_batch(batch_size)
            feed_dict = {X: X_batch, Y: Y_batch}
            summary_str, _, loss_batch = sess.run([merged_summary_op, optimizer, loss], feed_dict=feed_dict)
            summary_writer.add_summary(summary_str, global_step=global_step.eval())
            total_loss += loss_batch
        print('Average loss epoch {0}: {1}'.format(i, total_loss / n_batches))
    summary_writer.close()
    print('Total time: {0} seconds'.format(time.time() - start_time))

    print('Optimization Finished!')  # should be around 0.35 after 25 epochs

    # test the model
    preds = tf.nn.softmax(logits)
    correct_preds = tf.equal(tf.argmax(preds, 1), tf.argmax(Y, 1))
    accuracy = tf.reduce_sum(tf.cast(correct_preds, tf.float32))

    n_batches = int(mnist.test.num_examples / batch_size)
    total_correct_preds = 0

    for i in range(n_batches):
        X_batch, Y_batch = mnist.test.next_batch(batch_size)
        accuracy_batch = sess.run(accuracy, feed_dict={X: X_batch, Y: Y_batch})
        total_correct_preds += accuracy_batch

    print('Accuracy {0}'.format(total_correct_preds / mnist.test.num_examples))