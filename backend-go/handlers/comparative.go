package handlers

import (
	"backend-go/database"
	"backend-go/models"
	"math"
	"time"

	"github.com/gofiber/fiber/v2"
)

func GetComparativeAnalysis(c *fiber.Ctx) error {
	startDateStr := c.Query("start_date")
	endDateStr := c.Query("end_date")
	platform := c.Query("platform") // Pode ser "meta", "google" ou vazio (omnichannel)

	if startDateStr == "" || endDateStr == "" {
		return c.Status(400).JSON(fiber.Map{"error": "start_date e end_date são obrigatórios"})
	}

	// 1. MÁQUINA DO TEMPO: Calcula exatamente o período anterior
	layout := "2006-01-02" // Formato padrão de data do Go
	startDate, err1 := time.Parse(layout, startDateStr)
	endDate, err2 := time.Parse(layout, endDateStr)
	
	if err1 != nil || err2 != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Formato de data inválido. Use YYYY-MM-DD"})
	}

	// Descobre quantos dias tem o período atual
	daysDiff := int(endDate.Sub(startDate).Hours() / 24)
	
	// Volta no tempo para pegar a mesma quantidade de dias pra trás
	prevEndDate := startDate.AddDate(0, 0, -1)
	prevStartDate := prevEndDate.AddDate(0, 0, -daysDiff)

	// 2. FUNÇÃO ATIRADORA DE ELITE: Busca os dados filtrados
	type Metrics struct {
		Spend   float64
		Revenue float64
		Clicks  int
		Roas    float64
	}

	getMetrics := func(start, end time.Time, plat string) Metrics {
		var m struct {
			Spend   float64
			Revenue float64
			Clicks  int
		}

		// A query base (usando a nossa tabela certa)
		query := database.DB.Model(&models.CampaignInsight{}).
			Select("COALESCE(SUM(spend), 0) as spend, COALESCE(SUM(revenue), 0) as revenue, COALESCE(SUM(clicks), 0) as clicks").
			Where("DATE(data) BETWEEN ? AND ?", start.Format(layout), end.Format(layout))

		// Se o front mandar a plataforma, a gente filtra!
		if plat == "meta" || plat == "facebook" {
			query = query.Where("LOWER(platform) LIKE ?", "%meta%")
		} else if plat == "google" {
			query = query.Where("LOWER(platform) LIKE ?", "%google%")
		}

		query.Scan(&m)

		roas := 0.0
		if m.Spend > 0 {
			roas = math.Round((m.Revenue/m.Spend)*100) / 100
		}

		return Metrics{
			Spend:   math.Round(m.Spend*100) / 100,
			Revenue: math.Round(m.Revenue*100) / 100,
			Clicks:  m.Clicks,
			Roas:    roas,
		}
	}

	// 3. BUSCA OS DOIS PERÍODOS
	currentMetrics := getMetrics(startDate, endDate, platform)
	prevMetrics := getMetrics(prevStartDate, prevEndDate, platform)

	// 4. CALCULADORA DE DELTA (%)
	calcDelta := func(current, prev float64) float64 {
		if prev == 0 {
			if current > 0 {
				return 100.0 // Crescimento infinito se antes era 0 e agora tem algo
			}
			return 0.0
		}
		delta := ((current - prev) / prev) * 100
		return math.Round(delta*100) / 100
	}

	// 5. RESPOSTA FINAL (Pronta pro seu Vue.js engolir)
	return c.JSON(fiber.Map{
		"period_current": fiber.Map{
			"start": startDate.Format(layout),
			"end":   endDate.Format(layout),
		},
		"period_previous": fiber.Map{
			"start": prevStartDate.Format(layout),
			"end":   prevEndDate.Format(layout),
		},
		"filter_applied": platform,
		"stats": fiber.Map{
			"Faturamento":  fiber.Map{"current": currentMetrics.Revenue, "prev": prevMetrics.Revenue, "delta": calcDelta(currentMetrics.Revenue, prevMetrics.Revenue)},
			"Investimento": fiber.Map{"current": currentMetrics.Spend, "prev": prevMetrics.Spend, "delta": calcDelta(currentMetrics.Spend, prevMetrics.Spend)},
			"ROAS":         fiber.Map{"current": currentMetrics.Roas, "prev": prevMetrics.Roas, "delta": calcDelta(currentMetrics.Roas, prevMetrics.Roas)},
			"Cliques":      fiber.Map{"current": float64(currentMetrics.Clicks), "prev": float64(prevMetrics.Clicks), "delta": calcDelta(float64(currentMetrics.Clicks), float64(prevMetrics.Clicks))},
		},
	})
}