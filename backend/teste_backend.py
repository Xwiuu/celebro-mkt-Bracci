import requests

print("📡 Iniciando Teste de Filtro por Data no Backend...")

url = "http://127.0.0.1:8000/api/v1/campaigns/"

# Vamos testar do dia 01/04 (hoje) até o fim do ano!
params = {
    "platform": "meta",
    "start_date": "2026-04-01",
    "end_date": "2026-12-31",
    "limit": 2000,
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    dados = response.json()

    campanhas = dados.get("data", dados) if isinstance(dados, dict) else dados

    print(f"\n📦 SUCESSO! Campanhas encontradas: {len(campanhas)}")

    total_gasto = sum(float(c.get("investimento_total", 0) or 0) for c in campanhas)
    print(f"💰 GASTO TOTAL SOMADO: R$ {total_gasto:,.2f}")
    print("---------------------------------------------------\n")

except Exception as e:
    print(f"❌ ERRO: {e}")
