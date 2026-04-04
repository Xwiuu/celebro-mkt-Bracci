package services

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strconv"

	"backend-go/database"
	"backend-go/models"
)

// Struct temporária só para mastigar o formato estranho que o Facebook devolve
type MetaGraphResponse struct {
	Data []struct {
		CampaignID  string `json:"campaign_id"`
		DateStart   string `json:"date_start"`
		Spend       string `json:"spend"`       // O FB manda os números como string!
		Clicks      string `json:"clicks"`
		Impressions string `json:"impressions"`
	} `json:"data"`
}

func SyncMetaCampaigns() error {
	// 1. Pega os tokens do seu arquivo .env
	accessToken := os.Getenv("META_ACCESS_TOKEN")
	adAccountID := os.Getenv("META_AD_ACCOUNT_ID")

	if accessToken == "" || adAccountID == "" {
		return fmt.Errorf("credenciais da Meta não encontradas no .env")
	}

	// 2. Monta a URL da Graph API (buscando gastos, cliques e impressões dos últimos 7 dias)
	url := fmt.Sprintf("https://graph.facebook.com/v19.0/act_%s/insights?fields=campaign_id,spend,clicks,impressions&time_preset=last_7d&access_token=%s", adAccountID, accessToken)

	// 3. Faz o disparo (GET)
	resp, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("erro ao bater na API do Facebook: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)

	// 4. Converte o JSON do Facebook pra nossa struct temporária
	var fbData MetaGraphResponse
	if err := json.Unmarshal(body, &fbData); err != nil {
		return fmt.Errorf("erro ao decodificar JSON do Facebook: %v", err)
	}

	// 5. Salva no nosso "Arquivo de Aço" (Postgres)
	for _, item := range fbData.Data {
		// Convertendo as strings do FB para os números do nosso Go
		spend, _ := strconv.ParseFloat(item.Spend, 64)
		clicks, _ := strconv.Atoi(item.Clicks)
		impressions, _ := strconv.Atoi(item.Impressions)

		insight := models.CampaignInsight{
			CampaignID:  item.CampaignID,
			Data:        item.DateStart, 
			Spend:       spend,
			Revenue:     0, // Faturamento no FB (Purchases) exige um field a mais, zerei pra simplificar agora
			Clicks:      clicks,
			Impressions: impressions,
			Platform:    "meta",
		}

		// O comando 'Save' atualiza se já existir, ou cria se for novo
		result := database.DB.Create(&insight)
		if result.Error != nil {
			fmt.Printf("⚠️ Erro ao salvar campanha %s: %v\n", insight.CampaignID, result.Error)
		}
	}

	fmt.Println("✅ Sincronização com Meta concluída com sucesso!")
	return nil
}