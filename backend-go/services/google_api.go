package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"backend-go/database"
	"backend-go/models"
)

type GoogleAuthResponse struct {
	AccessToken string `json:"access_token"`
}

type GoogleAdsRequest struct {
	Query     string `json:"query"`
	PageToken string `json:"pageToken,omitempty"`
}

type GoogleAdsResponse struct {
	Results []struct {
		Campaign struct {
			Id   int64  `json:"id,string"`
			Name string `json:"name"`
		} `json:"campaign"`
		Segments struct {
			Date                     string `json:"date"`
			ConversionActionCategory string `json:"conversionActionCategory"` // 👈 O Filtro Mágico
		} `json:"segments"`
		Metrics struct {
			CostMicros       string  `json:"costMicros"`
			ConversionsValue float64 `json:"conversionsValue"`
			Clicks           string  `json:"clicks"`
			Impressions      string  `json:"impressions"`
		} `json:"metrics"`
	} `json:"results"`
	NextPageToken string `json:"nextPageToken"`
}

func getGoogleAccessToken() (string, error) {
	data := url.Values{}
	data.Set("client_id", os.Getenv("GOOGLE_ADS_CLIENT_ID"))
	data.Set("client_secret", os.Getenv("GOOGLE_ADS_CLIENT_SECRET"))
	data.Set("refresh_token", os.Getenv("GOOGLE_ADS_REFRESH_TOKEN"))
	data.Set("grant_type", "refresh_token")

	resp, err := http.PostForm("https://oauth2.googleapis.com/token", data)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var auth GoogleAuthResponse
	if err := json.NewDecoder(resp.Body).Decode(&auth); err != nil {
		return "", err
	}
	return auth.AccessToken, nil
}

func SyncGoogleDaily() error {
	hoje := time.Now().Format("2006-01-02")
	seteDias := time.Now().AddDate(0, 0, -7).Format("2006-01-02")
	return fetchAndSaveGoogle(seteDias, hoje)
}

func SyncGoogleHistory() error {
	hoje := time.Now().Format("2006-01-02")
	return fetchAndSaveGoogle("2023-01-01", hoje)
}

func fetchAndSaveGoogle(startDate string, endDate string) error {
	customerID := strings.ReplaceAll(os.Getenv("GOOGLE_ADS_CUSTOMER_ID"), "-", "")
	devToken := os.Getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
	loginCustomerID := strings.ReplaceAll(os.Getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"), "-", "")

	if customerID == "" || devToken == "" {
		return fmt.Errorf("credenciais do Google não encontradas no .env")
	}

	accessToken, err := getGoogleAccessToken()
	if err != nil || accessToken == "" {
		return fmt.Errorf("erro ao gerar token: %v", err)
	}

	urlAPI := fmt.Sprintf("https://googleads.googleapis.com/v23/customers/%s/googleAds:search", customerID)

	// Estrutura para montar o quebra-cabeça na memória do Go
	type dailyData struct {
		Spend       float64
		Revenue     float64
		Clicks      int
		Impressions int
		Name        string
	}
	consolidatedData := make(map[string]*dailyData)

	// Função interna para disparar as duas Queries
	runGAQL := func(query string, isConversionQuery bool) error {
		pageToken := ""
		pageCount := 1

		for {
			reqBody := GoogleAdsRequest{Query: query, PageToken: pageToken}
			jsonBody, _ := json.Marshal(reqBody)

			req, _ := http.NewRequest("POST", urlAPI, bytes.NewBuffer(jsonBody))
			req.Header.Set("Authorization", "Bearer "+accessToken)
			req.Header.Set("developer-token", devToken)
			if loginCustomerID != "" {
				req.Header.Set("login-customer-id", loginCustomerID)
			}
			req.Header.Set("Content-Type", "application/json")

			client := &http.Client{}
			resp, err := client.Do(req)
			if err != nil {
				return err
			}

			body, _ := io.ReadAll(resp.Body)
			resp.Body.Close()

			if resp.StatusCode != 200 {
				return fmt.Errorf("erro na API: %s", string(body))
			}

			var gaData GoogleAdsResponse
			json.Unmarshal(body, &gaData)

			for _, row := range gaData.Results {
				campID := fmt.Sprintf("%d", row.Campaign.Id)
				key := campID + "_" + row.Segments.Date

				if _, exists := consolidatedData[key]; !exists {
					consolidatedData[key] = &dailyData{Name: row.Campaign.Name}
				}

				if isConversionQuery {
					// 🛡️ O FILTRO ANTI-LIXO: Só entra se for PURCHASE (Compra)!
					if row.Segments.ConversionActionCategory == "PURCHASE" {
						if row.Metrics.ConversionsValue < 50000 { // Teto de sanidade
							consolidatedData[key].Revenue += row.Metrics.ConversionsValue
						}
					}
				} else {
					costMicros, _ := strconv.ParseFloat(row.Metrics.CostMicros, 64)
					clicks, _ := strconv.Atoi(row.Metrics.Clicks)
					impressions, _ := strconv.Atoi(row.Metrics.Impressions)

					consolidatedData[key].Spend = costMicros / 1000000.0
					consolidatedData[key].Clicks = clicks
					consolidatedData[key].Impressions = impressions
					if row.Campaign.Name != "" {
						consolidatedData[key].Name = row.Campaign.Name
					}
				}
			}

			if gaData.NextPageToken == "" {
				break
			}
			pageToken = gaData.NextPageToken
			pageCount++
		}
		return nil
	}

	fmt.Println("🚀 Puxando Gastos, Cliques e Impressões...")
	gaqlCore := fmt.Sprintf(`
		SELECT campaign.id, campaign.name, segments.date, metrics.cost_micros, metrics.clicks, metrics.impressions
		FROM campaign 
		WHERE segments.date BETWEEN '%s' AND '%s' AND metrics.cost_micros > 0`, startDate, endDate)
	
	if err := runGAQL(gaqlCore, false); err != nil {
		return err
	}

	fmt.Println("🚀 Puxando Faturamento filtrado por Compras Reais...")
	gaqlConv := fmt.Sprintf(`
		SELECT campaign.id, segments.date, segments.conversion_action_category, metrics.conversions_value
		FROM campaign 
		WHERE segments.date BETWEEN '%s' AND '%s' AND metrics.conversions_value > 0`, startDate, endDate)
	
	if err := runGAQL(gaqlConv, true); err != nil {
		return err
	}

	fmt.Println("💾 Injetando dados limpos no Banco de Dados...")
	for key, data := range consolidatedData {
		parts := strings.Split(key, "_")
		if len(parts) != 2 {
			continue
		}

		insight := models.GoogleCampaignInsight{
			CampaignID:   parts[0],
			CampaignName: data.Name,
			Data:         parts[1],
			Spend:        data.Spend,
			Revenue:      data.Revenue,
			Clicks:       data.Clicks,
			Impressions:  data.Impressions,
			Platform:     "google",
			DataRegistro: time.Now(),
		}

		database.DB.Where(models.GoogleCampaignInsight{CampaignID: insight.CampaignID, Data: insight.Data}).
			Assign(insight).
			FirstOrCreate(&models.GoogleCampaignInsight{})
	}

	fmt.Println("🏆 Histórico do Google Ads sincronizado e 100% BLINDADO!")
	return nil
}