package services

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"time"

	"backend-go/database"
	"backend-go/models"
)

type MetaAction struct {
	ActionType string `json:"action_type"`
	Value      string `json:"value"`
}

type MetaGraphResponse struct {
	Data []struct {
		CampaignID   string       `json:"campaign_id"`
		CampaignName string       `json:"campaign_name"`
		DateStart    string       `json:"date_start"`
		Spend        string       `json:"spend"`
		Clicks       string       `json:"clicks"`
		Impressions  string       `json:"impressions"`
		ActionValues []MetaAction `json:"action_values"`
	} `json:"data"`
	Paging struct {
		Next string `json:"next"`
	} `json:"paging"`
}

func SyncMetaDaily() error {
	return fetchAndSaveMeta("last_7d", "")
}

func SyncMetaHistory() error {
	// 1. Pega a data de hoje dinamicamente (2026)
	hoje := time.Now().Format("2006-01-02")

	// 2. Cria o JSON do time_range usando crases (backticks) 
	// Isso evita erros de aspas e garante que o JSON chegue perfeito na Meta
	timeRangeJSON := fmt.Sprintf(`{"since":"2025-12-07","until":"%s"}`, hoje)

	fmt.Printf("⏳ Iniciando busca histórica: de 2025-12-07 até %s\n", hoje)
	
	return fetchAndSaveMeta("", timeRangeJSON)
}
func fetchAndSaveMeta(timePreset string, timeRange string) error {
	accessToken := os.Getenv("META_ACCESS_TOKEN")
	adAccountID := os.Getenv("META_AD_ACCOUNT_ID")

	if accessToken == "" || adAccountID == "" {
		return fmt.Errorf("credenciais da Meta não encontradas no .env")
	}

	// Montando os parâmetros da requisição
	params := url.Values{}
	params.Add("fields", "campaign_id,campaign_name,spend,clicks,impressions,action_values")
	params.Add("time_increment", "1")
	params.Add("level", "campaign")
	params.Add("access_token", accessToken)

	if timeRange != "" {
		params.Set("time_range", timeRange)
	} else {
		params.Set("time_preset", timePreset)
	}

	// Montando a URL blindada
	url := fmt.Sprintf("https://graph.facebook.com/v19.0/act_%s/insights?%s", adAccountID, params.Encode())

	pageCount := 1

	for url != "" {
		resp, err := http.Get(url)
		if err != nil {
			return fmt.Errorf("erro ao bater na API: %v", err)
		}

		body, _ := io.ReadAll(resp.Body)
		resp.Body.Close()

		if resp.StatusCode != 200 {
			return fmt.Errorf("a Meta recusou a conexão! Status: %d - Motivo: %s", resp.StatusCode, string(body))
		}

		var fbData MetaGraphResponse
		if err := json.Unmarshal(body, &fbData); err != nil {
			return fmt.Errorf("erro no JSON: %v", err)
		}

		if len(fbData.Data) == 0 {
			break
		}

		for _, item := range fbData.Data {
			spend, _ := strconv.ParseFloat(item.Spend, 64)
			clicks, _ := strconv.Atoi(item.Clicks)
			impressions, _ := strconv.Atoi(item.Impressions)

			var revenue float64 = 0
			for _, action := range item.ActionValues {
				if action.ActionType == "purchase" || action.ActionType == "offsite_conversion.fb_pixel_purchase" {
					val, _ := strconv.ParseFloat(action.Value, 64)
					revenue += val
				}
			}

			insight := models.CampaignInsight{
				CampaignID:   item.CampaignID,
				CampaignName: item.CampaignName,
				Data:         item.DateStart,
				Spend:        spend,
				Revenue:      revenue,
				Clicks:       clicks,
				Impressions:  impressions,
				Platform:     "meta",
				DataRegistro: time.Now(),
			}

			database.DB.Where(models.CampaignInsight{CampaignID: insight.CampaignID, Data: insight.Data}).
				Assign(insight).
				FirstOrCreate(&models.CampaignInsight{})
		}

		fmt.Printf("✅ Página %d salva (com datas rígidas)...\n", pageCount)
		pageCount++

		// 🟢 ADICIONE O TIME.SLEEP AQUI
		// Verificamos se existe uma próxima página antes de esperar
		if fbData.Paging.Next != "" {
			fmt.Println("⏳ Aguardando 5 segundos para respeitar os limites da API...")
			time.Sleep(5 * time.Second)
		}

		url = fbData.Paging.Next 
	}

	fmt.Printf("🏆 Histórico ABSOLUTO sincronizado com sucesso!\n")
	return nil
}