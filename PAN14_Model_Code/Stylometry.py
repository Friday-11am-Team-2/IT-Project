# Necessary Imports
# Most code is rearranged or copied from the PAN14_data_demo.ipynb source code
#  and adapted to work as a callable library that loads existing models

### Required imports ###
import os
import json
import math
import csv
import numpy as np
import glob
import pickle
import itertools
from collections import Counter

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import tensorflow as tf
from tensorflow import keras
#from tensorflow.keras import layers
#from tensorflow.keras.layers import Dense, Dropout
#from tensorflow.keras.models import Sequential
#from tensorflow.keras.optimizers import Adam
#from tensorflow.keras.optimizers.schedules import PolynomialDecay
#from tensorflow.keras.callbacks import EarlyStopping

import gensim
from gensim.models import Word2Vec
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.test.utils import common_texts
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from scipy.spatial.distance import cosine
from sklearn.svm import SVC
from sklearn.model_selection import KFold
from collections import defaultdict

#import networkx as nx
#import random
#from tqdm import tqdm
#from urllib.request import urlretrieve
#import matplotlib.pyplot as plt
import string

### Environment Setup ###
def setupNltk():
	nltk.data.path = [ f"{os.getcwd()}/nltk_data"]
	nltk.download(["punkt", "stopwords","wordnet"], download_dir=nltk.data.path[0])


### Classes and library functions ###
class StyloNet:
	WORD2VEC_DEFAULT_PATH = "Word2Vec.model"
	BASENET_DEFAULT_CHECKPOINTS = "model_weights"

	### Setup functions ###
	def __init__(self, modelPath = BASENET_DEFAULT_CHECKPOINTS, w2vPath = WORD2VEC_DEFAULT_PATH):
		# Load Word2Vec
		self.word2vec = gensim.models.Word2Vec.load(w2vPath)

		# Load SiameseNet
		self.siamese_model : SiameseNet = buildSiameseNet(modelPath)
		self.base_network, self.clf_network = self.siamese_model.base, self.siamese_model.clf

	### Helper Functions ###
	def _vectorize(self,known,unknown):
		vectors = {
			'known': get_vectors(known,self.word2vec),
			'unknown': get_vectors(unknown,self.word2vec)
		}
		return vectors
	
	def _concatenate(self, vectors):
		known_feature_vectors = self.base_network.predict(np.array(vectors['known']), verbose=0)
		unknown_feature_vectors = self.base_network.predict(np.array(vectors['unknown']), verbose=0)

		author_representation = np.mean(known_feature_vectors, axis=0)
		unknown_representation = np.mean(unknown_feature_vectors, axis=0)

		concat_vec = np.concatenate((author_representation, unknown_representation), axis=None)
		return concat_vec

	### Interface Functions ###
	def predict(self, data : dict):
		if type(data) != dict: raise TypeError("Input must be in the form of a Dictionary!")

		vectors = self._vectorize(data['known'], data['unknown'])
		concats = self._concatenate(vectors)

		prediction = self.clf_network.predict(np.array([concats]))
		return prediction[0][0]
	
	def getInstance(self):
		return StyloInstance(self)

class StyloInstance():
	def __init__(self, parent : StyloNet):
		self.known = []
		self.unknown = None
		self.result = None
		self.parent = parent

	def addKnown(self, data):
		self.known.append(strip_text(data))

	def setUnknown(self, data):
		self.unknown = strip_text(data)
		self.result = None  # Reset result

	def addUnknownToProfile(self):
		if type(self.unknown) is None: raise ValueError("No unknown text loaded!")
		self.known.append(self.unknown)
		self.unknown = None
		self.result = None

	def getPrediction(self):
		if self.result is None:
			data = { 'known': self.known, 'unknown': self.unknown }
			self.result = self.parent.predict(data)
		return self.result


### External Text Helper Functions ###
W2V_VECTOR_SIZE = 300

def strip_text(data):
	if type(data) is str: data = data.splitlines()

	text = []
	for line in data:
		if type(line) is not str: line = str(line)
		cleaned = line.strip().lstrip("\ufeff")
		text.append(cleaned)

	return text

def preprocess_text(text):
    """
    Preprocess a given text by tokenizing, removing punctuation and numbers,
    removing stop words, and lemmatizing.

    Args:
        text (str): The text to preprocess.

    Returns:
        list: The preprocessed text as a list of tokens.
    """
    if not isinstance(text, str):
        text = str(text)

    # Tokenize the text into words
    tokens = word_tokenize(text.lower())

    # Remove punctuation and numbers
    table = str.maketrans('', '', string.punctuation + string.digits)
    tokens = [word.translate(table) for word in tokens]

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if (not word in stop_words) and (word != '')]

    # Lemmatize words
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    return tokens

def convert_text_to_vector(texts, model):
    """
    Convert a list of texts into their corresponding word2vec vectors
    """
    vectors = []
    for text in texts:
        words = preprocess_text(text)
        vector = np.sum([model.wv[word] for word in words if word in model.wv], axis=0)
        word_count = np.sum([word in model.wv for word in words])
        if word_count != 0:
            vector /= word_count
        else:
          vector = np.zeros(W2V_VECTOR_SIZE)
        vectors.append(vector)
    return vectors

def count_punctuations(texts):
  """
  Count the frequency of different punctuations in the texts
  """
  # Define punctuations to count
  punctuations = set(['.', ',', ';', ':', '!', '?', '-', '(', ')', '\"', '\'', '`', '/'])

  # Initialize dictionary to count punctuations
  punctuations_count = {p: 0 for p in punctuations}

  # Count punctuations in text_list
  for text in texts:
      for char in text:
          if char in punctuations:
              punctuations_count[char] += 1

  # Return list of punctuation counts
  return list(punctuations_count.values())

def analyze_sentence_lengths(sentences):
	"""
	Analyze the lengths of sentences
	"""
	sentence_lengths = [len(sentence.split()) for sentence in sentences]
	average_length = np.mean(sentence_lengths)
	count_over_avg = np.sum([length > average_length for length in sentence_lengths])
	count_under_avg = np.sum([length < average_length for length in sentence_lengths])
	count_avg = len(sentence_lengths) - count_over_avg - count_under_avg

	return [count_over_avg, count_under_avg, count_avg, average_length]

def analyze_words(texts):
	"""
	Analyze the words used in the texts
	"""
	words = []
	stop_words = set(stopwords.words('english'))
	lemmatizer = WordNetLemmatizer()
	for text in texts:
		tokenized = word_tokenize(text.lower())
		processed = [lemmatizer.lemmatize(word) for word in tokenized if word not in stop_words]
		words += processed
	word_freq = nltk.FreqDist(words)
	rare_count = np.sum([freq <= 2 for word, freq in word_freq.items()])
	long_count = np.sum([len(word) > 6 for word in words])
	word_lengths = [len(word) for word in words]
	average_length = np.mean(word_lengths)
	count_over_avg = np.sum([length > average_length for length in word_lengths])
	count_under_avg = np.sum([length < average_length for length in word_lengths])
	count_avg = len(word_lengths) - count_over_avg - count_under_avg
	ttr = len(set(words)) / len(words) if words else 0

	return [rare_count, long_count, count_over_avg, count_under_avg, count_avg, ttr]

def calculate_style_vector(texts):
	"""
	Calculate the style vector of the texts
	"""
	punctuation_vec = count_punctuations(texts)     # Punctuations stylistic features
	sentence_vec = analyze_sentence_lengths(texts)  # Sentences stylistic features
	word_vec = analyze_words(texts)                 # Words stylistic features
	word_count = np.sum([len(text.split()) for text in texts])

	vector = np.concatenate((punctuation_vec, sentence_vec, word_vec))

	return vector / word_count if word_count else vector

def get_vectors(texts, w2v_model):
	res = []
	for text in texts:
		w2v_vec = np.mean(convert_text_to_vector(text, w2v_model), axis=0)
		style_vec = calculate_style_vector(text)
		res.append(np.concatenate((w2v_vec, style_vec), axis=None))
		# res.append(w2v_vec)

	return res


### SiameseNet class and functions ###
class SiameseNet(tf.keras.Model):
	# SiameseNet model declaration from PAN14_data_demo.ipynb
	def __init__(self, base_network, clf_network):
		super().__init__()
		self.base = base_network
		self.clf = clf_network

	def call(self, inputs):
		anchor = inputs[0]
		positive = inputs[1]
		negative = inputs[2]

		output_anchor = self.base(anchor)
		output_positive = self.base(positive)
		output_negative = self.base(negative)

		# Anchor - Positive
		x1 = tf.concat([output_anchor, output_positive], axis=-1)
		x1_out = self.clf(x1)

		# Anchor - Negative
		x2 = tf.concat([output_anchor, output_negative], axis=-1)
		x2_out = self.clf(x2)

		return (x1_out, x2_out)
	
def create_dense_block(x, units, dropout_rate, l1_reg, l2_reg):
	x = tf.keras.layers.Dense(units, kernel_regularizer=tf.keras.regularizers.l1_l2(l1=l1_reg, l2=l2_reg))(x)
	x = tf.keras.layers.BatchNormalization()(x)
	x = tf.keras.layers.Activation('relu')(x)
	return tf.keras.layers.Dropout(dropout_rate)(x)

def create_base_network(embedding_dim, dropout_rate=0.4, l1_reg=0.001, l2_reg=0.001):
	input = tf.keras.layers.Input(shape=embedding_dim)
	x = tf.keras.layers.BatchNormalization()(input)

	x = create_dense_block(x, 256, dropout_rate, l1_reg, l2_reg)
	x = create_dense_block(x, 128, dropout_rate, l1_reg, l2_reg)
	x = create_dense_block(x, 64, dropout_rate, l1_reg, l2_reg)

	x = tf.keras.layers.Dense(64, activation='linear')(x)

	return tf.keras.Model(inputs=input, outputs=x)

def create_clf_network(input_shape, dropout_rate=0.5, l1_reg=0.003, l2_reg=0.003):
	input = tf.keras.layers.Input(shape=(input_shape,))
	x = tf.keras.layers.BatchNormalization()(input)

	x = create_dense_block(x, 128, dropout_rate, l1_reg, l2_reg)
	x = create_dense_block(x, 64, dropout_rate, l1_reg, l2_reg)
	x = create_dense_block(x, 32, dropout_rate, l1_reg, l2_reg)

	x = tf.keras.layers.Dense(1, activation='sigmoid')(x)

	return tf.keras.Model(inputs=input, outputs=x)

def customer_loss(y_true, y_pred):
    AP = y_pred[0]
    AN = y_pred[1]

    loss = 1.0 - AP + AN

    return loss

# Constant representing the shape of the input numpy array.
# Normally derived from training data, but the value is always the same.
def buildSiameseNet(path):
	"""Construct the SiameseNet model from an existing weights dir"""
	EMBEDDING_DIM = (323,)
	
	# Create the base network
	embedding_dim = EMBEDDING_DIM

	base_network = create_base_network(embedding_dim)
	clf_network = create_clf_network(base_network.output_shape[1]*2)

	siamese_model = SiameseNet(base_network, clf_network)

	# Assemble the model
	siamese_model.compile(optimizer='adam', loss=customer_loss)

	# Load weights
	checkpoint_dir = path
	checkpoint_path = f"{path}/cp.ckpt"

	cp_save = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
					      save_weights_only=True,
						  verbose=1)

	latest = tf.train.latest_checkpoint(checkpoint_dir)
	siamese_model.load_weights(latest)
	
	clf_network.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.AUC()])
	
	return siamese_model

### Run-on-import ###
setupNltk()