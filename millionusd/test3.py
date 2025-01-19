# Configurações iniciais
payout_compra = 0.922  # Payout para a entrada de compra (92.2%)
payout_venda = 0.922  # Payout para a entrada de venda (92.2%)


# Função para calcular lucros com base nas entradas
def calcular_lucros(entrada_compra, payout_compra, payout_venda):
    entrada_venda = (entrada_compra * payout_compra) / payout_venda
    lucro_compra = (entrada_compra * payout_compra) - entrada_venda
    lucro_venda = (entrada_venda * payout_venda) - entrada_compra
    return entrada_compra, entrada_venda, lucro_compra, lucro_venda


# Função para encontrar o E1 ideal ou o mais próximo do ideal
def encontrar_entrada_ideal(payout_compra, payout_venda, step=0.01, limite=10000):
    melhor_entrada = None
    menor_diferenca = float('inf')  # Começa com uma diferença infinita
    maior_lucro_total = float('-inf')  # Para garantir que lucros sejam positivos

    # Testa valores de E1 (entrada_compra) entre 1 e o limite
    entrada_compra = 1
    while entrada_compra <= limite:
        _, entrada_venda, lucro_compra, lucro_venda = calcular_lucros(entrada_compra, payout_compra, payout_venda)

        # Verifica se os lucros são positivos
        if lucro_compra > 0 and lucro_venda > 0:
            # Calcula a diferença entre os lucros
            diferenca = abs(lucro_compra - lucro_venda)

            # Atualiza se a configuração for mais equilibrada ou maior lucro total
            if diferenca < menor_diferenca or (
                    diferenca == menor_diferenca and min(lucro_compra, lucro_venda) > maior_lucro_total):
                menor_diferenca = diferenca
                maior_lucro_total = min(lucro_compra, lucro_venda)
                melhor_entrada = (entrada_compra, entrada_venda, lucro_compra, lucro_venda)

        entrada_compra += step  # Incrementa o valor de E1 para buscar o ótimo

    return melhor_entrada


# Executa a otimização
resultado = encontrar_entrada_ideal(payout_compra, payout_venda)

# Mostra os resultados
if resultado:
    entrada_compra, entrada_venda, lucro_compra, lucro_venda = resultado
    print("Entrada ideal ou mais próxima encontrada:")
    print(f"Entrada Compra (E1): {entrada_compra:.2f}")
    print(f"Entrada Venda (E2): {entrada_venda:.2f}")
    print("\nLucros calculados:")
    print(f"Lucro no caso de vitória da compra: {lucro_compra:.2f}")
    print(f"Lucro no caso de vitória da venda: {lucro_venda:.2f}")
else:
    print("Nenhuma configuração ideal foi encontrada, mesmo aproximada.")
