import nltk
import spacy

# Downloading the model
spacy.cli.download("en_core_web_sm")

# Download required NLTK data files
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')