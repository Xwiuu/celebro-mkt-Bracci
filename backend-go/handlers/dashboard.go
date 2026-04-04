package handlers

import (
	"fmt"
	"math"
	"time"

	"backend-go/database"
	"backend-go/models"

	"github.com/gofiber/fiber/v2"
)

// Estruturas auxiliares para o JSON de Resposta
type MetricDelta struct {
	Current float64 `json:"current"`
	Prev    float64 `json:"prev"`
	Delta   float64 `json:"delta"`
}

type Period struct {
	Start string `json:"start"`
	End   string `json:"end"`
}

func GetDashboardSummary(c *fiber.Ctx) error {
	// Pega as datas que o Vue enviou
	startDate := c.Query("start_date")
	endDate := c.Query("end_date")

	if startDate == "" || endDate == "" {
		return c.Status(400).JSON(fiber.Map{"error": "start_date e end_date são obrigatórios"})
	}

	// ---------------------------------------------------------
	// 0. CÁLCULO INTELIGENTE DO PERÍODO ANTERIOR
	// ---------------------------------------------------------
	layout := "2006-01-02"
	start, err := time.Parse(layout, startDate)
	end, err2 := time.Parse(layout, endDate)
	if err != nil || err2 != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Formato de data inválido. Use YYYY-MM-DD"})
	}

	// Quantos dias o usuário selecionou?
	daysFiltered := int(end.Sub(start).Hours() / 24)
	
	// Recua o tempo exato para o período anterior
	prevEnd := start.AddDate(0, 0, -1)
	prevStart := prevEnd.AddDate(0, 0, -daysFiltered)

	prevStartDateStr := prevStart.Format(layout)
	prevEndDateStr := prevEnd.Format(layout)

	// ---------------------------------------------------------
	// 1. KPIs GERAIS (PERÍODO ATUAL vs ANTERIOR)
	// ---------------------------------------------------------
	type KPI struct {
		TotalSpend       float64
		TotalRevenue     float64
		TotalClicks      float64 // Mudado para float64 para facilitar os deltas
		TotalImpressions float64
	}

	var kpisCurrent KPI
	var kpisPrev KPI

	// Query do Período ATUAL
	database.DB.Model(&models.CampaignInsight{}).
		Select("COALESCE(SUM(spend), 0) as total_spend, COALESCE(SUM(revenue), 0) as total_revenue, COALESCE(SUM(clicks), 0) as total_clicks, COALESCE(SUM(impressions), 0) as total_impressions").
		Where("DATE(data) BETWEEN ? AND ?", startDate, endDate).
		Scan(&kpisCurrent)

	// Query do Período ANTERIOR
	database.DB.Model(&models.CampaignInsight{}).
		Select("COALESCE(SUM(spend), 0) as total_spend, COALESCE(SUM(revenue), 0) as total_revenue, COALESCE(SUM(clicks), 0) as total_clicks, COALESCE(SUM(impressions), 0) as total_impressions").
		Where("DATE(data) BETWEEN ? AND ?", prevStartDateStr, prevEndDateStr).
		Scan(&kpisPrev)

	// Regras de Negócio: ROAS
	calcRoas := func(revenue, spend float64) float64 {
		if spend > 0 {
			return revenue / spend
		}
		return 0
	}

	roasCurrent := calcRoas(kpisCurrent.TotalRevenue, kpisCurrent.TotalSpend)
	roasPrev := calcRoas(kpisPrev.TotalRevenue, kpisPrev.TotalSpend)

	// Regras de Negócio: Delta (%)
	calcDelta := func(curr, prev float64) float64 {
		if prev > 0 {
			return math.Round((((curr - prev) / prev) * 100) * 100) / 100
		}
		if curr > 0 {
			return 100.0 // Crescimento total se antes era 0
		}
		return 0.0
	}

	// ---------------------------------------------------------
	// 2. DADOS DO GRÁFICO (Crescimento Diário por Plataforma - Período Atual)
	// ---------------------------------------------------------
	type ChartRow struct {
		Data     string
		Platform string
		Spend    float64
	}

	var rawRows []ChartRow

	database.DB.Model(&models.CampaignInsight{}).
		Select("CAST(DATE(data) AS TEXT) as data, platform, SUM(spend) as spend").
		Where("DATE(data) BETWEEN ? AND ?", startDate, endDate).
		Group("DATE(data), platform").
		Order("DATE(data) asc").
		Scan(&rawRows)

	chartSeries := make(map[string]map[string]float64)

	for _, r := range rawRows {
		dateStr := r.Data
		if len(dateStr) > 10 {
			dateStr = dateStr[:10]
		}

		if chartSeries[dateStr] == nil {
			chartSeries[dateStr] = map[string]float64{"meta": 0, "google": 0}
		}

		if r.Platform == "meta" || r.Platform == "Meta" || r.Platform == "facebook" {
			chartSeries[dateStr]["meta"] += r.Spend
		} else {
			chartSeries[dateStr]["google"] += r.Spend
		}
	}

	// ---------------------------------------------------------
	// 3. RANKING OMNICHANNEL (Top 10 Campanhas que mais geraram Captado)
	// ---------------------------------------------------------
	type RankingRow struct {
		Name     string  `json:"name"`
		Platform string  `json:"platform"`
		Spend    float64 `json:"spend"`
		Revenue  float64 `json:"revenue"`
		Roas     float64 `json:"roas"`
	}

	var ranking []RankingRow

	database.DB.Model(&models.CampaignInsight{}).
		Select("campaign_id as name, platform, SUM(spend) as spend, SUM(revenue) as revenue").
		Where("DATE(data) BETWEEN ? AND ?", startDate, endDate).
		Where("revenue > 0").
		Group("campaign_id, platform").
		Order("SUM(revenue) DESC"). // Atualizado para ordenar pelo captado!
		Limit(10).
		Scan(&ranking)

	for i := range ranking {
		if ranking[i].Spend > 0 {
			roas_cru := ranking[i].Revenue / ranking[i].Spend
			ranking[i].Roas = math.Round(roas_cru*100) / 100
		}
	}

	// Print de sucesso no terminal do servidor
	fmt.Printf("✅ SUCESSO! Delta Calculado: Atual (%s a %s) vs Anterior (%s a %s)\n", startDate, endDate, prevStartDateStr, prevEndDateStr)

	// ---------------------------------------------------------
	// 4. RETORNO DA API
	// ---------------------------------------------------------
	return c.JSON(fiber.Map{
		"period_current": Period{Start: startDate, End: endDate},
		"period_previous": Period{Start: prevStartDateStr, End: prevEndDateStr},
		"stats": fiber.Map{
			"Captado": MetricDelta{
				Current: kpisCurrent.TotalRevenue,
				Prev:    kpisPrev.TotalRevenue,
				Delta:   calcDelta(kpisCurrent.TotalRevenue, kpisPrev.TotalRevenue),
			},
			"Investimento": MetricDelta{
				Current: kpisCurrent.TotalSpend,
				Prev:    kpisPrev.TotalSpend,
				Delta:   calcDelta(kpisCurrent.TotalSpend, kpisPrev.TotalSpend),
			},
			"ROAS": MetricDelta{
				Current: math.Round(roasCurrent*100) / 100,
				Prev:    math.Round(roasPrev*100) / 100,
				Delta:   calcDelta(roasCurrent, roasPrev),
			},
			"Cliques": MetricDelta{
				Current: kpisCurrent.TotalClicks,
				Prev:    kpisPrev.TotalClicks,
				Delta:   calcDelta(kpisCurrent.TotalClicks, kpisPrev.TotalClicks),
			},
		},
		"chart_series": chartSeries,
		"ranking":      ranking,
	})
}