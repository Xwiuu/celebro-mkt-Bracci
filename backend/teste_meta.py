import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

# Carrega as chaves do teu .env
load_dotenv()

APP_ID = os.getenv('META_APP_ID')
APP_SECRET = os.getenv('META_APP_SECRET')
ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')

print("Iniciando conexão com a Matrix...")

try:
    # Liga o motor
    FacebookAdsApi.init(access_token=ACCESS_TOKEN)

    # Arruma o prefixo da conta caso o CLI tenha esquecido
    if not ACCOUNT_ID.startswith('act_'):
        ACCOUNT_ID = f"act_{ACCOUNT_ID}"

    print(f"Buscando na conta: {ACCOUNT_ID}")

    # Puxa os dados brutos sem filtro nenhum
    account = AdAccount(ACCOUNT_ID)
    campaigns = account.get_campaigns(fields=['id', 'name'])
    
    print(f"\n🔥 BINGO! O trator encontrou {len(campaigns)} campanhas.")
    
    for camp in campaigns[:5]: # Mostra só as 5 primeiras pra não poluir a tela
        print(f"ID: {camp['id']} | Nome: {camp.get('name', 'Sem nome')}")

except Exception as e:
    print(f"\n❌ ERRO CABULOSO (O que o CLI tava escondendo):")
    print(e)