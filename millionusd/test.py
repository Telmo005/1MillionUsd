# Configurações iniciais
payout_compra = 0.922  # Payout para a entrada de compra (92.2%)
payout_venda = 0.922  # Payout para a entrada de venda (92.2%)

# Função para calcular as entradas equilibradas
def calcular_entradas_equilibradas(payout_compra, payout_venda):
    # Fixamos um dos valores (E1) para calcular o outro (E2)
    entrada_compra = 1000  # Valor inicial para a compra (pode ser ajustado)

    # Resolvendo para entrada_venda (E2)
    entrada_venda = (entrada_compra * payout_compra) / (1 + payout_venda)

    # Retornamos as entradas calculadas
    return entrada_compra, entrada_venda

# Cálculo
entrada_compra, entrada_venda = calcular_entradas_equilibradas(payout_compra, payout_venda)

# Resultados
lucro_compra = (entrada_compra * payout_compra) - entrada_venda
lucro_venda = (entrada_venda * payout_venda) - entrada_compra

print("Entradas calculadas para equilíbrio:")
print(f"Entrada Compra (E1): {entrada_compra:.2f}")
print(f"Entrada Venda (E2): {entrada_venda:.2f}")
print("\nResultados:")
print(f"Lucro no caso de vitória da compra: {lucro_compra:.2f}")
print(f"Lucro no caso de vitória da venda: {lucro_venda:.2f}")
