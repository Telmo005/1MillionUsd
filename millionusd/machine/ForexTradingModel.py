import pandas as pd
import talib
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


class ForexTradingModel:
    def __init__(self):
        self.model = None

    def prepare_data(self, candles):
        """
        Prepara os dados dos candles para o treinamento do modelo.

        :param candles: Lista de objetos Candle
        :return: X (features) e y (target)
        """
        if not candles:
            print("Nenhum dado de candle para preparar.")
            return None, None

        # Converter lista de objetos Candle em DataFrame
        data = {
            'open': [c.open_price for c in candles],
            'close': [c.close_price for c in candles],
            'min': [c.min_price for c in candles],
            'max': [c.max_price for c in candles]
        }
        df = pd.DataFrame(data)

        # Adicionar indicadores técnicos
        df['SMA_20'] = talib.SMA(df['close'], timeperiod=20)
        df['RSI_14'] = talib.RSI(df['close'], timeperiod=14)
        df = df.dropna()

        # Definir o alvo (exemplo: se o preço vai subir ou descer)
        df['target'] = (df['close'] > df['open']).astype(int)

        # Definir recursos e alvo
        features = ['SMA_20', 'RSI_14']
        X = df[features]
        y = df['target']

        return X, y

    def train_model(self, X, y):
        """
        Treina o modelo com os dados fornecidos.

        :param X: Features
        :param y: Target
        """
        if X is None or y is None:
            print("Dados inválidos para treinamento.")
            return

        # Dividir os dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Treinar o modelo
        self.model = DecisionTreeClassifier()
        self.model.fit(X_train, y_train)

        # Fazer previsões e avaliar o modelo
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {accuracy * 100:.2f}%")

    def predict(self, X):
        """
        Faz previsões usando o modelo treinado.

        :param X: Dados para previsão
        :return: Previsões
        """
        if self.model is None:
            raise ValueError("Modelo não treinado. Execute o método 'train_model' primeiro.")
        return self.model.predict(X)
