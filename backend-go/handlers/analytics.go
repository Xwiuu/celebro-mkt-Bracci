package handlers

import (
	"backend-go/database"
	"github.com/gofiber/fiber/v2"
	"time"
)

// Estrutura do JSON que o Vue.js vai receber
type DashboardStats struct {
	TotalSpend       float64 `json:"total_spend"`
	TotalRevenue     float64 `json:"total_revenue"`
	TotalClicks      int     `json:"total_clicks"`
	TotalImpressions int     `json:"total_impressions"`
	ROAS             float64 `json:"roas"`
	CTR              float64 `json:"ctr"`
	CPC              float64 `json:"cpc"`
}

// Estrutura interna para ler do banco
type Aggregates struct {
	Spend       float64
	Revenue     float64
	Clicks      int
	Impressions int
}

func GetMarketingPerformance(c *fiber.Ctx) error {
	// 🟢 Mudança: Pegar datas dinâmicas. Se o front não mandar, ele calcula os últimos 30 dias.
	hoje := time.Now()
	trintaDiasAtras := hoje.AddDate(0, 0, -30).Format("2006-01-02")
	hojeStr := hoje.Format("2006-01-02")

	startDate := c.Query("start_date", trintaDiasAtras)
	endDate := c.Query("end_date", hojeStr)

	type CampaignRow struct {
		Name     string  `json:"name"`
		Revenue  float64 `json:"revenue"`
		Spend    float64 `json:"spend"`
		Roas     float64 `json:"roas"`
		Platform string  `json:"platform"`
	}

	type ChartPoint struct {
		Date    string  `json:"date"`
		Revenue float64 `json:"revenue"`
	}

	var meta Aggregates
	var google Aggregates

	// 1. TOTAIS GERAIS
	database.DB.Table("fb_campaign_insights").
		Select("COALESCE(SUM(spend), 0) as spend, COALESCE(SUM(revenue), 0) as revenue, COALESCE(SUM(clicks), 0) as clicks, COALESCE(SUM(impressions), 0) as impressions").
		Where("data >= ? AND data <= ?", startDate, endDate).
		Scan(&meta)
	database.DB.Table("google_campaign_insights").
		Select("COALESCE(SUM(spend), 0) as spend, COALESCE(SUM(revenue), 0) as revenue, COALESCE(SUM(clicks), 0) as clicks, COALESCE(SUM(impressions), 0) as impressions").
		Where("data >= ? AND data <= ?", startDate, endDate).
		Scan(&google)

	// 2. RANKING (TOP 5)
	var ranking []CampaignRow
	database.DB.Table("fb_campaign_insights").
		Select("campaign_name as name, SUM(revenue) as revenue, SUM(spend) as spend, 'meta' as platform").
		Where("data >= ? AND data <= ?", startDate, endDate).
		Group("campaign_name").
		Order("revenue DESC").
		Limit(5).
		Scan(&ranking)

	var googleRank []CampaignRow
	database.DB.Table("google_campaign_insights").
		Select("campaign_name as name, SUM(revenue) as revenue, SUM(spend) as spend, 'google' as platform").
		Where("data >= ? AND data <= ?", startDate, endDate).
		Group("campaign_name").
		Order("revenue DESC").
		Limit(5).
		Scan(&googleRank)

	ranking = append(ranking, googleRank...)
	for i := range ranking {
		if ranking[i].Spend > 0 {
			ranking[i].Roas = ranking[i].Revenue / ranking[i].Spend
		}
	}

	// 📊 3. SÉRIE TEMPORAL PARA O GRÁFICO
	var metaSeries []ChartPoint
	database.DB.Table("fb_campaign_insights").
		Select("data as date, SUM(revenue) as revenue").
		Where("data >= ? AND data <= ?", startDate, endDate).
		Group("data").
		Order("data ASC").
		Scan(&metaSeries)

	var googleSeries []ChartPoint
	database.DB.Table("google_campaign_insights").
		Select("data as date, SUM(revenue) as revenue").
		Where("data >= ? AND data <= ?", startDate, endDate).
		Group("data").
		Order("data ASC").
		Scan(&googleSeries)

	chartSeries := make(map[string]map[string]float64)
	for _, p := range metaSeries {
		if _, ok := chartSeries[p.Date]; !ok {
			chartSeries[p.Date] = make(map[string]float64)
		}
		chartSeries[p.Date]["meta"] = p.Revenue
	}
	for _, p := range googleSeries {
		if _, ok := chartSeries[p.Date]; !ok {
			chartSeries[p.Date] = make(map[string]float64)
		}
		chartSeries[p.Date]["google"] = p.Revenue
	}

	// 4. RESPOSTA FINAL
	totalSpend := meta.Spend + google.Spend
	totalRevenue := meta.Revenue + google.Revenue
	var roas float64
	if totalSpend > 0 {
		roas = totalRevenue / totalSpend
	}

	return c.JSON(fiber.Map{
		"status": "sucesso",
		"consolidado": fiber.Map{
			"total_spend":       totalSpend,
			"total_revenue":     totalRevenue,
			"roas":              roas,
			"total_clicks":      meta.Clicks + google.Clicks,
			"total_impressions": meta.Impressions + google.Impressions,
		},
		"ranking":      ranking,
		"chart_series": chartSeries,
	})
}