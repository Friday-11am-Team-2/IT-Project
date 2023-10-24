# Most code is from the PAN14_data_demo.ipynb source code, either copied or adapted (as annotated)
# the StyloNet class encapsulates the entire model and can be call to make predictions on text datasets

### Required imports ###
import os
import json
import string
import gensim
import tensorflow as tf
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk
import numpy as np

# Lambda for print out module name/version
ver = lambda module: print(f"{__name__} loading: {module.__name__}=={module.__version__}")

if __debug__:
    ver(np)
    ver(nltk)
    ver(tf)
    ver(gensim)
else:
    # Restrict tensorflow logging to only critical events
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

### Classes (for use outside the module) ###
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

    def __init__(self, profile: str = None, profile_dir: str = "stylometry_models"):
        # Load the profile path (if no profile is specified, use the current directory)
        profile_path = os.path.join(profile_dir, profile) if profile else os.curdir

        if profile and not os.path.isdir(profile_dir):
            raise FileNotFoundError("Profile directory doesn't exist!")

        # Try loading the manifest, else use default values
        try:
            with open(os.path.join(profile_path, "manifest.json"), "rb") as f:
                manifest = json.load(f)
        except FileNotFoundError:
            # If the manifest isn't there, set to an empty dictionary to use defaults
            manifest = {}

        # Load metadata and paths (with defaults as fallback)
        self.valid_threshold = manifest.get("valid_threshold", 0.5)
        embedding_dim = (manifest.get('embedding_dim', 323),) if isinstance(manifest.get('embedding_dim', 323), int) else tuple(manifest.get('embedding_dim', 323))

        nltk_path = os.path.join(profile_path, manifest.get("nltk_data", "nltk_data"))
        w2v_save = os.path.join(profile_path, manifest.get("word2vec", "word2vec.model"))
        model_checkpoints = os.path.join(profile_path, manifest.get("ckpts", "model_weights/cp.ckpt"))

        # Load Word2Vec model
        self.word2vec = loadW2v(w2v_save)

        # Define the SiameseNet model and load the weights from checkpoints
        self.siamese_model = buildSiameseNet(model_checkpoints, embedding_dim)
        self.base_network = self.siamese_model.base
        self.clf_network = self.siamese_model.clf

        # Setup path for NLTK and ensure required packages are downloaded
        setup_nltk(nltk_path)

    def _vectorize(self, text: dict) -> dict:
        """Use Word2Vec model to generate text vectors"""
        vectors = {
            'known': get_vectors(text['known'], self.word2vec),
            'unknown': get_vectors(text['unknown'], self.word2vec)
        }
        return vectors

    def _vectorize_multi(self, texts: list[dict]) -> list[dict]:
        vectors = []
        for text in texts:
            vectors.append(self._vectorize(text))
        return vectors

    def _concatenate(self, vectors: dict):
        known_feature_vectors = self.base_network.predict(np.array(vectors['known']), verbose=0)
        unknown_feature_vectors = self.base_network.predict(np.array(vectors['unknown']), verbose=0)

        author_representation = np.mean(known_feature_vectors, axis=0)
        unknown_representation = np.mean(unknown_feature_vectors, axis=0)

        concat_vec = np.concatenate((author_representation, unknown_representation), axis=None)
        return concat_vec

    def _concatenate_multi(self, vectors: list[dict]):
        concats = []
        for vec in vectors:
            concats.append(self._concatenate(vec))
        return np.array(concats)

    ### Interface Functions ###
    def score(self, texts: dict) -> float:
        """Run the model and return the similarity score as a decimal"""
        if len(texts['unknown']) == 0:
            return 0  # Incase of empty unknown set

        vectors = self._vectorize(texts)  # Run Word2Vec
        concats = self._concatenate(vectors)  # Run base_network

        # Run clf_network
        prediction = self.clf_network.predict(np.expand_dims(concats, axis=0), verbose=0)

        # Convert to numpy array and flatten, as output shape will be (1,1)
        return unwrap(prediction)

    def score_batch(self, texts: list|dict) -> list[float]|dict:
        """Calculate score over a list or dictionary of texts and return a list/dict of the results"""

        # Return a key/value pair generator for both a list and existing dictionary
        def unpack(texts): return texts.items() if type(texts) is dict else enumerate(data)

        # Check whether a value is valid input (i.e. it's unknown text is non-empty)
        def good_input(text): return type(text['unknown']) is list and len(text['unknown']) != 0

        # Convert input to a dictionary, if not already.
        # Ensures bad input can be filtered out and given a 0.0 rating at the end
        data = {k: v for k, v in unpack(texts) if good_input(v)}
        # Important for list ordering and including all keys in dictionaries

        # Run the predictions (usually tensorflow batch functions where possible)
        vectors = self._vectorize_multi(data.values())
        concates = self._concatenate_multi(vectors)
        predictions = {k: unwrap(v) for k, v in zip(data.keys(), self.clf_network.predict(concates, verbose=0))}

        # Format the output (unwrapping already done above)
        if isinstance(texts, list):
            results = [predictions.get(x, 0.0) for x in range(len(texts))]
        else:
            results = {k: predictions.get(k, 0.0) for k in texts.keys()}

        return results

    def predict(self, texts: dict) -> tuple[bool, float]:
        """Calculate score and return a prediction based on the predetermined threshold, returns a boolean result"""
        score = self.score(texts)
        result = score >= self.valid_threshold
        return (result, score)

    def predict_batch(self, texts: list|dict) -> list[bool]|dict:
        """Run predict over a list/dict of texts and return the result with a boolean result"""
        scores = self.score_batch(texts)
        def pred(s): return s >= self.valid_threshold

        if type(texts) is dict:
            results = {}
            for key, val in scores.items():
                results[key] = pred(val)
        else:
            results = []
            for val in scores:
                results.append(pred(val))

        return results


class TextAnalytics:
    """Processes the input text, and provides style analysis functions"""
    def __init__(self, text: str|list):
        # Text as a single string
        self.text:str = strip_text(text)

        # remove punctuation, tokenize, filter out stop words and lemmatize
        self.keywords:list[str] = preprocess_text(self.text)

        # tokenize by sentence, remove punctuation and calculate lengths
        self.sentences:list[str] = [ sent.translate(str.maketrans('', '', string.punctuation)) for sent in sent_tokenize(self.text) ]
        self.sentence_lengths:list[int]  = [ len(sent.split()) for sent in self.sentences ]

        # generate a frequency distribution of all keywords
        self.word_freqs = nltk.FreqDist(self.keywords)

    def rare_words_freq(self, rare_threshold = 2) -> float:
        """Based on the 'analyze_words' function.
        Return the frequency of rare words, words used > 2 times (by default), in the text"""
        count = np.sum([ freq <= rare_threshold for _, freq in self.word_freqs.items() ])
        return count / len(self.keywords)

    def long_words_freq(self, long_threshold = 6) -> float:
        """ Based on 'analyze_words' function.
        Percentage score of long words (> 6 characters by default) in the text"""
        count = np.sum([ len(word) > long_threshold for word in self.keywords ])
        return count / len(self.keywords)

    def sentence_length_avg(self) -> float:
        """Calcuate average sentence length"""
        return np.mean(self.sentence_lengths)

    def sentence_length_distrib(self) -> tuple:
        """ Based on the sentence lengths section of 'analyze_sentence_lengths'.
        Return a distribution of sentence lengths, relative to the rounded avg, in form
        (below, equal, above)"""
        avg = round(np.mean(self.sentence_lengths))

        above = np.sum([ length > avg for length in self.sentence_lengths ]) / len(self.sentence_lengths)
        below = np.sum([ length < avg for length in self.sentence_lengths ]) / len(self.sentence_lengths)
        equals = (len(self.sentence_lengths) - above - below) / len(self.sentence_lengths)

        return (below, equals, above)

    def sentence_count(self) -> int:
        """Counts  the number of sentences in the text"""
        return len(self.sentence_lengths)

    def most_common_words(self, num = 5) -> list[str]:
        """List the top 5 (default) more common words in the text"""
        return self.word_freqs.most_common(num)

    def word_count(self) -> int:
        """Total word count for the text"""
        return len(word_tokenize(self.text))

    def word_length_avg(self) -> float:
        """Average word length"""
        return np.mean([len(word) for word in word_tokenize(self.text)])


### Utility functions ###
# Both imported from the original source code, or rewritten


def setup_nltk(path=f"{os.curdir}/nltk_data") -> None:
    """Set up the NLTK package path and downloads datapacks (if required)"""
    if path:
        nltk.data.path = [path]
        
    nltk.download(["punkt", "stopwords","wordnet"], nltk.data.path[0], quiet=True)

def unwrap(var):
    """Function to extract variables nested inside single-element lists/arrays"""
    is_array = lambda var: isinstance(var, (list, tuple, set, np.ndarray))
    while is_array(var) and len(var) == 1: var = var[0]

    return var


def flatten(var: list) -> str:
    """Convert string arrays, of any depth, into a raw string.
        Any joins are separated with newlines."""
    if isinstance(var, str): return var

    res = ""
    for i in var:
        nextstr = f'{i}\n' if isinstance(i, str) else flatten(i)
        res = res + nextstr if res else nextstr

    return res.strip()
      

def strip_text(data: list|str, split=False) -> str|list[str]:
    """Strip whitespace from text data and format by separating lines,
        'split' determines whether output is split into individual lines."""
    
    # Eliminate multi-dimensional arrays of strings
    data = flatten(data) if isinstance(data, list) else data

    # Ensure strings are split along new-lines
    data = data.splitlines() if isinstance(data, str) else data

    text = []
    for line in data:
        cleaned = line.strip().lstrip("\ufeff")

        if len(cleaned) == 0:
            # Eliminate empty lines
            continue

        text.append(cleaned)

    text = '\n'.join(text) if not split else text

    return text


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
def buildSiameseNet(checkpoint_file: str, embedding_dim: tuple = (323,)) -> SiameseNet:
    """Construct the SiameseNet model using code from PAN14_data_demo.ipynb using saved weights at checkpoint_dir
        embedding_dim defines the input shape for the model, the default from the build process is (323,None)"""

    # Create sub-model frame
    base_network = create_base_network(embedding_dim)
    clf_network = create_clf_network(base_network.output_shape[1]*2)

    # Create main model frame
    siamese_model = SiameseNet(base_network, clf_network)

    # Compile models
    siamese_model.compile(optimizer='adam', loss=customer_loss)
    clf_network.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.AUC()])

    siamese_model.load_weights(checkpoint_file).expect_partial()

    return siamese_model


def loadW2v(path: str) -> gensim.models.Word2Vec:
    """Load a pre-saved gensim Word2Vec model from file"""
    return gensim.models.Word2Vec.load(path)


### Text Processing ###
def preprocess_text(text: list | str) -> list[str]:
    """
    Text preprocessor from PAN14_Data_Demo.ipnyb,
    with some changes to handle more complex input

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


def convert_text_to_vector(texts: list, model: gensim.models.Word2Vec) -> list:
    """
    Text vectorizing function from PAN14_Data_Demo.ipynb
    Convert a list of texts into their corresponding word2vec vectors
    """
    vectors = []
    for text in texts:
        words = preprocess_text(text)
        vector = np.sum([model.wv[word]for word in words if word in model.wv], axis=0)
        word_count = np.sum([word in model.wv for word in words])
        if word_count != 0:
            vector /= word_count
        else:
            vector = np.zeros(model.vector_size)
        vectors.append(vector)
    return vectors


def count_punctuations(texts) -> list[int]:
    """
    count_punctuations func from PAN14_Data_Demo.ipynb
    Count the frequency of different punctuations in the texts
    """
    # Define punctuations to count
    punctuations = set(['.', ',', ';', ':', '!', '?', '-','(', ')', '\"', '\'', '`', '/'])

    # Initialize dictionary to count punctuations
    punctuations_count = {p: 0 for p in punctuations}

    # Count punctuations in text_list
    for text in texts:
        for char in text:
            if char in punctuations:
                punctuations_count[char] += 1

    # Return list of punctuation counts
    return list(punctuations_count.values())


def analyze_sentence_lengths(text):
    """
    analyze_sentence_lengths from PAN14_Data_Demo.ipynb
    Analyze the lengths of sentences.
    Modifed to operate on a text instead of 'sentences', as
    the value passed to the function in calcuate_style_vector is just the text
    """
    # Use NLTK sentence tokenizer instead of splitting by line
    sentences = sent_tokenize(text)

    sentence_lengths = [len(sentence.split()) for sentence in sentences]
    average_length = np.mean(sentence_lengths)
    count_over_avg = np.sum([length > average_length for length in sentence_lengths])
    count_under_avg = np.sum([length < average_length for length in sentence_lengths])
    count_avg = len(sentence_lengths) - count_over_avg - count_under_avg

    return [count_over_avg, count_under_avg, count_avg, average_length]


def analyze_words(text):
    """
    anaylze_words from PAN14_Data_Demo.ipynb
    Analyze the words used in the texts.
    Modified to operate on a single text at a time.
    """
    #words = []
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    # Previously a for loop to iterate over all texts.
    # However function is only actually called on a single text
    tokenized = word_tokenize(text.lower())
    processed = [lemmatizer.lemmatize(word) for word in tokenized if word not in stop_words]
    words = processed

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

def calculate_style_vector(text):
    """
    calculate_style_vector from PAN14_Data_Demo.ipynb
    Calculate the style vector of the texts
    """
    punctuation_vec = count_punctuations(text)     # Punctuations stylistic features
    sentence_vec = analyze_sentence_lengths(text)  # Sentences stylistic features
    word_vec = analyze_words(text)                 # Words stylistic features
    word_count = len(word_tokenize(text))

    vector = np.concatenate((punctuation_vec, sentence_vec, word_vec))

    return vector / word_count if word_count else vector


def get_vectors(texts: list, w2v_model: gensim.models.Word2Vec) -> list:
    """get_vectors from PAN14_Data_Demo.ipynb"""
    res = []
    for text in texts:
        clean_text = strip_text(text)
        w2v_vec = np.mean(convert_text_to_vector(clean_text, w2v_model), axis=0)
        style_vec = calculate_style_vector(clean_text)
        res.append(np.concatenate((w2v_vec, style_vec), axis=None))
        # res.append(w2v_vec)

    return res
