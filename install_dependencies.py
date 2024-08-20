import nltk
import subprocess

# Download required NLTK data files
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('words')
nltk.download('stopwords')
nltk.download('wordnet')

def install_dependencies():
    #subprocess.check_call(["pip", "install", "--no-cache-dir", "-r", "spacy==2.3.5"])
    #subprocess.check_call(["pip", "install", "spacy==2.3.5"])
    subprocess.check_call(["pip", "install", "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz"])

if __name__ == "__main__":
    install_dependencies()

