package models

type CampaignInsight struct {
	ID          uint    `gorm:"primaryKey" json:"id"`
	CampaignID  string  `json:"campaign_id"`
	Data        string  `json:"data"` 
	Spend       float64 `json:"spend"`
	Revenue     float64 `json:"revenue"`
	Clicks      int     `json:"clicks"`
	Impressions int     `json:"impressions"`
	Platform    string  `json:"platform"`
}

// 🎯 O TIRO DE SNIPER: Nome exato da tabela!
func (CampaignInsight) TableName() string {
	return "fb_campaign_insights"
}