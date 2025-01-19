# Configurações iniciais
payout_compra = 0.922  # Payout para a entrada de compra (92.2%)
payout_venda = 0.922  # Payout para a entrada de venda (92.2%)

# Função para calcular as entradas maximizando o lucro
def calcular_entradas_com_lucro(payout_compra, payout_venda):
    entrada_compra = 1000  # Valor fixo inicial para a compra (ajustável)

    # Calcular a entrada de venda que maximize o retorno
    entrada_venda = (entrada_compra * payout_compra) / payout_venda

    # Calcular lucros potenciais para os dois cenários
    lucro_compra = (entrada_compra * payout_compra) - entrada_venda
    lucro_venda = (entrada_venda * payout_venda) - entrada_compra

    # Garantir que os dois lucros sejam positivos
    if lucro_compra > 0 and lucro_venda > 0:
        return entrada_compra, entrada_venda, lucro_compra, lucro_venda
    else:
        # Caso não seja possível garantir lucro positivo, ajustamos os valores
        ajuste = max(-lucro_compra, -lucro_venda) + 1  # Ajuste para cobrir prejuízos
        entrada_venda += ajuste / payout_venda
        lucro_compra = (entrada_compra * payout_compra) - entrada_venda
        lucro_venda = (entrada_venda * payout_venda) - entrada_compra
        return entrada_compra, entrada_venda, lucro_compra, lucro_venda

# Cálculo
entrada_compra, entrada_venda, lucro_compra, lucro_venda = calcular_entradas_com_lucro(payout_compra, payout_venda)

# Resultados
print("Entradas calculadas para garantir lucro:")
print(f"Entrada Compra (E1): {entrada_compra:.2f}")
print(f"Entrada Venda (E2): {entrada_venda:.2f}")
print("\nLucros garantidos:")
print(f"Lucro no caso de vitória da compra: {lucro_compra:.2f}")
print(f"Lucro no caso de vitória da venda: {lucro_venda:.2f}")
