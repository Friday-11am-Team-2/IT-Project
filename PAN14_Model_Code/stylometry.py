# Most code is from the PAN14_data_demo.ipynb source code, either copied or adapted (as annotated)
# the StyloNet class encapsulates the entire model and can be call to make predictions on text datasets

### Required imports ###
import os
#import math
#import glob
#import pickle
#import json
import string

# Lambda for print out module name/version
ver = lambda module : print(f"{__name__} loading: {module.__name__}=={module.__version__}")

import numpy as np
ver(np)

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
ver(nltk)

# Restrict tensorflow logging to only critical events
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
#from tensorflow import keras
#from tensorflow.keras import layers
#from tensorflow.keras.layers import Dense, Dropout
#from tensorflow.keras.models import Sequential
#from tensorflow.keras.optimizers import Adam
#from tensorflow.keras.optimizers.schedules import PolynomialDecay
#from tensorflow.keras.callbacks import EarlyStopping
ver(tf)

import gensim
#from gensim.models import Word2Vec
#from gensim.models.doc2vec import Doc2Vec, TaggedDocument
#from gensim.test.utils import common_texts
ver(gensim)

#import sklearn
#from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
#from sklearn.model_selection import train_test_split, GridSearchCV
#from sklearn.preprocessing import MinMaxScaler, StandardScaler
#from sklearn.metrics.pairwise import cosine_similarity
#from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.linear_model import LogisticRegression
#from sklearn.cluster import KMeans
#from sklearn.svm import SVC
#from sklearn.model_selection import KFold
#ver(sklearn)

#import scipy
#from scipy.spatial.distance import cosine


### Classes (for use outside the model) ###
class StyloNet:
	"""Contains the whole stylometry model, functions score, score_multi, predict and predict_multi
		can be called to run the stylometry model on a text.

		Input format for predictions is the following:
			texts = {
				'known': list[str] (known text(s))
				'unknown': list[str] (unknown text(s))
			}
		All lists for texts can be multi-dimensional, as long as it only ends in strings
	"""

	def __init__(self, working_dir:str = os.curdir, valid_threshold:float = 0.5,
					model_checkpoints:str = "model_weights/cp.ckpt", w2v_save:str = "Word2Vec.model", nltk_path:str = "nltk_data"):

		# Most args can be left at their default values, as long as working_dir is correct the model should work.
		if not os.path.isdir(working_dir):
			raise OSError(f"Working dir for StyloNet does not exist: {working_dir}")

		setupNltk(os.path.join(working_dir, nltk_path))

		# Load Word2Vec model
		self.word2vec = loadW2v(os.path.join(working_dir, w2v_save))

		# Redefine and load the SiameseNet model from checkpoints
		self.siamese_model = buildSiameseNet(os.path.join(working_dir, model_checkpoints))
		self.base_network, self.clf_network = self.siamese_model.base, self.siamese_model.clf

		# Save validiy threshold for making predictions
		self.threshold = valid_threshold

	def _vectorize(self,text : dict):
		vectors = {
			'known': get_vectors(text['known'],self.word2vec),
			'unknown': get_vectors(text['unknown'],self.word2vec)
		}
		return vectors

	def _vectorize_multi(self, texts: list[dict]):
		vectors = []
		for text in texts:
			vectors.append(self._vectorize(text))
		return vectors

	def _concatenate(self, vectors: dict):
		known_feature_vectors = self.base_network(np.array(vectors['known']))
		unknown_feature_vectors = self.base_network(np.array(vectors['unknown']))

		author_representation = np.mean(known_feature_vectors, axis=0)
		unknown_representation = np.mean(unknown_feature_vectors, axis=0)

		concat_vec = np.concatenate((author_representation, unknown_representation), axis=None)
		return concat_vec

	def _concatenate_multi(self, vectors : list[dict]):
		concats = []
		for vec in vectors:
			concats.append(self._concatenate(vec))
		return np.array(concats)

	### Interface Functions ###
	def score(self, texts : dict) -> float:
		"""Run the model and return the similarity score as a decimal"""
		if len(texts['unknown']) == 0: return 0  # Incase of empty unknown set

		vectors = self._vectorize(texts)
		concats = self._concatenate(vectors)

		prediction : tf.Tensor = self.clf_network(np.array([concats]))
		if prediction.shape != (1,1): raise ValueError("Result incorrect shape!")

		# Convert to numpy array and flatten, as output shape will be (1,1)
		return prediction.numpy()[0][0]

	def score_batch(self, texts: list|dict) -> list[float]|dict:
		"""Calculate score over a list or dictionary of texts and return a list/dict of the results"""

		# Return a key/value pair generator for both a list and existing dictionary
		unpack = lambda texts: texts.items() if type(texts) is dict else enumerate(data)

		# Check whether a value is valid input (i.e. it's unknown text is non-empty)
		good_input = lambda text: type(text['unknown']) is list and len(text['unknown']) != 0

		# Convert input to a dictionary, if not already.
		# Ensures bad input can be filtered out and given a 0.0 rating at the end
		data = { k: v for k, v in unpack(texts) if good_input(v) }
		# Important for list ordering and including all keys in dictionaries

		# Run the predictions
		vectors = self._vectorize_multi(data.values())
		concates = self._concatenate_multi(vectors)
		predictions = { k: unwrap(v) for k, v in zip(data.keys(), self.clf_network.predict(concates, verbose=0)) }

		# Format the output (unwrapping already done above)
		if type(texts) is list:
			results = [ predictions.get(x, 0.0) for x in range(len(texts)) ]
		else:
			results = { k: predictions.get(k, 0.0) for k in texts.keys() }

		return results

	def predict(self, texts: dict) -> bool:
		"""Calculate score and return a prediction based on the predetermined threshold, returns a boolean result"""
		return self.score(texts) >= self.threshold

	def predict_batch(self, texts: list|dict) -> list[bool]|dict:
		"""Run predict over a list/dict of texts and return the result with a boolean result"""
		scores = self.score_batch(texts)
		pred = lambda s : s >= self.threshold

		if type(texts) is dict:
			results = {}
			for key, val in scores.items():
				results[key] = pred(val)
		else:
			results = []
			for val in scores:
				results.append(pred(val))

		return results

### Utility functions ###
# Both imported from the original source code, or rewritten. Not intended for use outside the module.
def setupNltk(path = f"{os.curdir}/nltk_data") -> None:
	"""Set up the NLTK package path and downloads datapacks (if required)"""
	nltk.data.path = [ path ]
	nltk.download(["punkt", "stopwords","wordnet"], nltk.data.path[0])

def unwrap(var):
	"""Function to extract variables nested inside 1-element lists/arrays"""
	is_array = lambda var : isinstance(var, (list, tuple, set, np.ndarray))
	while is_array(var) and len(var) == 1: var = var[0]
	return var

### Model Definition ###
class SiameseNet(tf.keras.Model):
	"""SiameseNet model declaration from PAN14_data_demo.ipynb"""
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
	
### Supporting functions to recreate the model ###
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

### Model Loading Functions ###
def buildSiameseNet(checkpoint_dir: str, embedding_dim: tuple = (323,)) -> SiameseNet:
	"""Construct the SiameseNet model using code from PAN14_data_demo.ipynb
		using saved weights at checkpoint_dir
		embedding_dim defines the input shape for the model, the default from the build process is (323,None)"""

	# Create sub-model frame
	base_network = create_base_network(embedding_dim)
	clf_network = create_clf_network(base_network.output_shape[1]*2)

	# Create main model frame
	siamese_model = SiameseNet(base_network, clf_network)
	siamese_model.compile(optimizer='adam', loss=customer_loss)

	# Compile clf model
	clf_network.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.AUC()])

	# Load model weights from checkpoint_dir
	latest = tf.train.latest_checkpoint(checkpoint_dir)
	siamese_model.load_weights(latest).expect_partial()
	
	return siamese_model

def loadW2v(path:str) -> gensim.models.Word2Vec:
	"""Load a pre-saved gensim Word2Vec model from file"""
	return gensim.models.Word2Vec.load(path)

### Text Processing ###
def strip_text(data: list|str) -> list[str]:
	"""Strip whitespace from text data line-by-line"""
	if type(data) is str: data = data.splitlines()

	text = []
	for line in data:
		# Flatten any more than 1D arrays of strings/chars
		if type(line) is not str: line = str(line)

		cleaned = line.strip().lstrip("\ufeff")
		text.append(cleaned)

	return text

def preprocess_text(text: list|str) -> list[str]:
    """
    Text preprocessor from PAN14_Data_Demo.ipnyb
    
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

def convert_text_to_vector(texts : list, model: gensim.models.Word2Vec, w2v_vector_size = 300) -> list:
    """
    Text vectorizing function from PAN14_Data_Demo.ipynb
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
          vector = np.zeros(w2v_vector_size)
        vectors.append(vector)
    return vectors

def count_punctuations(texts) -> list[int]:
  """
  count_punctuations func from PAN14_Data_Demo.ipynb
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
	analyze_sentence_lengths from PAN14_Data_Demo.ipynb
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
	anaylze_words from PAN14_Data_Demo.ipynb
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
	calculate_style_vector from PAN14_Data_Demo.ipynb
	Calculate the style vector of the texts
	"""
	punctuation_vec = count_punctuations(texts)     # Punctuations stylistic features
	sentence_vec = analyze_sentence_lengths(texts)  # Sentences stylistic features
	word_vec = analyze_words(texts)                 # Words stylistic features
	word_count = np.sum([len(text.split()) for text in texts])

	vector = np.concatenate((punctuation_vec, sentence_vec, word_vec))

	return vector / word_count if word_count else vector

def get_vectors(texts: list, w2v_model: gensim.models.Word2Vec) -> list:
	"""get_vectors from PAN14_Data_Demo.ipynb"""
	res = []
	for text in texts:
		w2v_vec = np.mean(convert_text_to_vector(text, w2v_model), axis=0)
		style_vec = calculate_style_vector(text)
		res.append(np.concatenate((w2v_vec, style_vec), axis=None))
		# res.append(w2v_vec)

	return res