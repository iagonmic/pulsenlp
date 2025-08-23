# Análise de sentimentos
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analysis_sentiment(text: str):

    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    compound = score['compound']

    if compound >= 0.05:
        return 'Positivo'
    
    if compound <= -0.05:
        return 'Negativo'
    
    return 'Neutro'