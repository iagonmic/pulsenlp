# Detecção de assuntos (LDA, embeddings, etc.)

from preprocessing import process

from gensim import corpora
from gensim.models.ldamodel import LdaModel

def detect_topic(text_list):
    # Pré-processamento dos textos para o LDA
    textos_processados = [process(text) for text in text_list]

    # Criação do dicionário e corpus
    dicionario = corpora.Dictionary(textos_processados)
    corpus = [dicionario.doc2bow(texto) for texto in textos_processados]

    # Treinamento do modelo LDA (com 3 tópicos de exemplo)
    lda_model = LdaModel(corpus=corpus, id2word=dicionario, num_topics=3, passes=10)

    # Análise do texto de interesse
    texto_para_analisar = process(text_list[0])
    bow_texto = dicionario.doc2bow(texto_para_analisar)
    topicos_texto = lda_model.get_document_topics(bow_texto)

    # Encontrando o tópico com a maior probabilidade
    topico_principal = max(topicos_texto, key=lambda x: x[1])

    # O tópico é um par (ID do tópico, Probabilidade).
    # Precisamos do ID para ver as palavras-chave do tópico.
    palavras_chave_topico = lda_model.print_topic(topico_principal[0], topn=5)
    
    return palavras_chave_topico.split('+')

text = ["Esse é um texto de teste para a minha aplicação", "Mais um teste para checagem de operação.", "O meu ventilador está quebrado.", "Como ser um cientista de dados excelente"]
detect_topic(text)