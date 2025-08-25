# Tokenização, normalização, stemming, lematização

import nltk
import re

from nltk import tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

def process(text: str):

    # Normalização
    text_normalized = text.lower()

    # Aplicando Regex
    text_regex = re.sub(r'[^a-z\s]', '', text_normalized)

    # Tokenização
    tokenized = tokenize.word_tokenize(text=text_regex, language='portuguese')

    # Removendo stopwords
    swords = stopwords.words('portuguese')
    text_without_stopwords = [token for token in tokenized if token not in swords]

    lemmatizer = WordNetLemmatizer()
    lemmas = [lemmatizer.lemmatize(token) for token in text_without_stopwords]

    return lemmas

text = "Eu amo programação! É muito bom programar"
print(process(text))