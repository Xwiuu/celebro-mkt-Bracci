package handlers

import (
	"backend-go/database"
	"math"
	"fmt"
	"time"
	"github.com/gofiber/fiber/v2"
)

func GetComparativeAnalysis(c *fiber.Ctx) error {
	startDateStr := c.Query("start_date")
	endDateStr := c.Query("end_date")
	layout := "2006-01-02"

	if startDateStr == "" || endDateStr == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Datas obrigatórias"})
	}

	startDate, _ := time.Parse(layout, startDateStr)
	endDate, _ := time.Parse(layout, endDateStr)
	daysDiff := int(endDate.Sub(startDate).Hours()/24) + 1

	prevEndDate := startDate.AddDate(0, 0, -1)
	prevStartDate := prevEndDate.AddDate(0, 0, -(daysDiff - 1))

	// Estruturas de suporte
	type MetricRow struct {
		Spend   float64
		Revenue float64
		Clicks  int
	}

	fetchData := func(start, end time.Time) (MetricRow, MetricRow, []float64) {
		var meta, google MetricRow
		database.DB.Table("fb_campaign_insights").Select("COALESCE(SUM(spend), 0), COALESCE(SUM(revenue), 0), COALESCE(SUM(clicks), 0)").
			Where("data BETWEEN ? AND ?", start.Format(layout), end.Format(layout)).Row().Scan(&meta.Spend, &meta.Revenue, &meta.Clicks)
		
		database.DB.Table("google_campaign_insights").Select("COALESCE(SUM(spend), 0), COALESCE(SUM(revenue), 0), COALESCE(SUM(clicks), 0)").
			Where("data BETWEEN ? AND ?", start.Format(layout), end.Format(layout)).Row().Scan(&google.Spend, &google.Revenue, &google.Clicks)

		// Busca série diária para o gráfico (soma das duas plataformas)
		var series []float64
		for i := 0; i < daysDiff; i++ {
			day := start.AddDate(0, 0, i).Format(layout)
			var dailyRev float64
			database.DB.Raw("SELECT (SELECT COALESCE(SUM(revenue), 0) FROM fb_campaign_insights WHERE data = ?) + (SELECT COALESCE(SUM(revenue), 0) FROM google_campaign_insights WHERE data = ?)", day, day).Scan(&dailyRev)
			series = append(series, dailyRev)
		}

		return meta, google, series
	}

	// 1. Busca os dados dos dois períodos
	currMeta, currGoogle, currSeries := fetchData(startDate, endDate)
	prevMeta, prevGoogle, prevSeries := fetchData(prevStartDate, prevEndDate)

	// Totais Consolidados
	currTotal := MetricRow{Spend: currMeta.Spend + currGoogle.Spend, Revenue: currMeta.Revenue + currGoogle.Revenue, Clicks: currMeta.Clicks + currGoogle.Clicks}
	prevTotal := MetricRow{Spend: prevMeta.Spend + prevGoogle.Spend, Revenue: prevMeta.Revenue + prevGoogle.Revenue, Clicks: prevMeta.Clicks + prevGoogle.Clicks}

	calcDelta := func(c, p float64) float64 {
		if p == 0 { return 100.0 }
		return math.Round(((c-p)/p)*10000) / 100
	}

	// 2. Breakdown de Plataformas (Share)
	metaShare := 0.0
	googleShare := 0.0
	if currTotal.Revenue > 0 {
		metaShare = math.Round((currMeta.Revenue / currTotal.Revenue) * 1000) / 10
		googleShare = 100 - metaShare
	}

	return c.JSON(fiber.Map{
		"status": "sucesso",
		"period_current":  fiber.Map{"start": startDateStr, "end": endDateStr},
		"period_previous": fiber.Map{"start": prevStartDate.Format(layout), "end": prevEndDate.Format(layout)},
		"stats": fiber.Map{
			"Faturamento":  fiber.Map{"current": currTotal.Revenue, "prev": prevTotal.Revenue, "delta": calcDelta(currTotal.Revenue, prevTotal.Revenue)},
			"Investimento": fiber.Map{"current": currTotal.Spend, "prev": prevTotal.Spend, "delta": calcDelta(currTotal.Spend, prevTotal.Spend)},
			"ROAS":         fiber.Map{"current": currTotal.Revenue/math.Max(1, currTotal.Spend), "prev": prevTotal.Revenue/math.Max(1, prevTotal.Spend), "delta": calcDelta(currTotal.Revenue/math.Max(1, currTotal.Spend), prevTotal.Revenue/math.Max(1, prevTotal.Spend))},
			"Cliques":      fiber.Map{"current": currTotal.Clicks, "prev": prevTotal.Clicks, "delta": calcDelta(float64(currTotal.Clicks), float64(prevTotal.Clicks))},
		},
		"platforms": []fiber.Map{
			{"name": "Meta Ads", "fat": currMeta.Revenue, "share": metaShare, "roas": currMeta.Revenue/math.Max(1, currMeta.Spend)},
			{"name": "Google Ads", "fat": currGoogle.Revenue, "share": googleShare, "roas": currGoogle.Revenue/math.Max(1, currGoogle.Spend)},
		},
		"chart_data": fiber.Map{
			"categories": generateLabels(daysDiff),
			"current":    currSeries,
			"previous":   prevSeries,
		},
	})
}

func generateLabels(n int) []string {
	labels := make([]string, n)
	for i := 0; i < n; i++ { labels[i] = fmt.Sprintf("Dia %d", i+1) }
	return labels
}