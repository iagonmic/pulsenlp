# Análise de sentimentos
from LeIA import SentimentIntensityAnalyzer

def sentiment_analysis(text: str):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    
    return score['compound']

if __name__ == "__main__":
    print(sentiment_analysis("Eu amo programação! É muito bom programar"))  # Exemplo de uso