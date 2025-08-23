# Análise de sentimentos
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analysis_sentiment(text: str):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    
    return score['compound']