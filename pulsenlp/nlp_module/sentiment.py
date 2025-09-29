from pysentimiento import create_analyzer

model = "pysentimiento/bertweet-pt-sentiment"

analyzer = create_analyzer(task="sentiment", lang="pt", model_name=model)

def sentiment_analysis(text: str) -> dict:
    result = analyzer.predict(text)

    return result.probas['POS'] - result.probas['NEG']


if __name__ == "__main__":
    # TESTE
    print(sentiment_analysis("O restaurante foi uma experiência deplorável. O atendimento foi lento e rude, os pratos chegaram frios e mal preparados, e a higiene do local deixava muito a desejar. Além disso, os preços eram absurdamente altos para a qualidade oferecida. Senti-me completamente enganado e decepcionado. Não recomendo a ninguém; foi um desperdício de tempo e dinheiro."))
    print(sentiment_analysis("O restaurante apresentou um serviço padrão. Os pratos estavam de acordo com o esperado, sem grandes destaques, e o atendimento foi dentro do normal, nem particularmente rápido nem lento. O ambiente estava razoavelmente limpo e os preços estavam na média do mercado. A experiência foi funcional, mas nada que se destaque de forma positiva ou negativa."))
    print(sentiment_analysis("O restaurante proporcionou uma experiência incrível! Cada prato era cuidadosamente preparado, delicioso e apresentado de forma impecável. O atendimento foi atencioso, rápido e cordial, fazendo com que eu me sentisse extremamente bem-vindo. O ambiente era limpo, aconchegante e agradável, e os preços, justos considerando a qualidade excepcional. Saí completamente satisfeito e com vontade de voltar o quanto antes. Recomendo a todos sem a menor dúvida!"))
