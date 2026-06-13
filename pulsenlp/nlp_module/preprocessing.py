import spacy
import re

nlp = spacy.load("pt_core_news_sm")

def process(text: str):
    # Normalização
    text_normalized = text.lower()

    # Aplicando Regex (mantendo só letras e espaços)
    text_regex = re.sub(r'[^a-záéíóúâêîôûãõç\s]', '', text_normalized)

    # Processando
    doc = nlp(text_regex)

    # Remover stopwords e tokens de pontuação, pegar lemas
    lemmas = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]

    return lemmas

def pos_tagging(text: str):
    doc = nlp(text)
    return [(token.text, token.pos_, token.tag_, spacy.explain(token.tag_)) for token in doc]

def noun_chunks(text: str):
    doc = nlp(text)
    return [chunk.text for chunk in doc.noun_chunks]

def named_entities(text: str):
    doc = nlp(text)
    return [(ent.text, ent.label_, spacy.explain(ent.label_)) for ent in doc.ents]

def sentence_segmentation(text: str):
    doc = nlp(text)
    return [sent.text for sent in doc.sents]

