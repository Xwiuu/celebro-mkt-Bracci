package models

import "time"

// --- ESTRUTURA DA META (Já existe) ---
type CampaignInsight struct {
	ID           string    `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`
	CampaignID   string    `json:"campaign_id"`
	CampaignName string    `json:"campaign_name"`
	Data         string    `json:"data"` 
	Spend        float64   `json:"spend"`
	Revenue      float64   `json:"revenue"`
	Clicks       int       `json:"clicks"`
	Impressions  int       `json:"impressions"`
	Platform     string    `json:"platform"`
	DataRegistro time.Time `gorm:"column:data_registro" json:"data_registro"`
}

func (CampaignInsight) TableName() string {
	return "fb_campaign_insights"
}

// 👇 ADICIONA ISTO: ESTRUTURA DO GOOGLE ADS 👇
type GoogleCampaignInsight struct {
	ID           string    `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`
	CampaignID   string    `json:"campaign_id"`
	CampaignName string    `json:"campaign_name"`
	Data         string    `json:"data"` 
	Spend        float64   `json:"spend"`
	Revenue      float64   `json:"revenue"`
	Clicks       int       `json:"clicks"`
	Impressions  int       `json:"impressions"`
	Platform     string    `json:"platform"`
	DataRegistro time.Time `gorm:"column:data_registro" json:"data_registro"`
}

// Diz ao Go qual é o nome exato da tabela na base de dados
func (GoogleCampaignInsight) TableName() string {
	return "google_campaign_insights"
}