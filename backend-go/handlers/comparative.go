package handlers

import (
    "backend-go/database"
    "math"
    "time"
    "github.com/gofiber/fiber/v2"
)

func GetComparativeAnalysis(c *fiber.Ctx) error {
    startDateStr := c.Query("start_date")
    endDateStr := c.Query("end_date")
    layout := "2006-01-02"

    if startDateStr == "" || endDateStr == "" {
        return c.Status(400).JSON(fiber.Map{"error": "Datas 'start_date' e 'end_date' são obrigatórias"})
    }

    startDate, err1 := time.Parse(layout, startDateStr)
    endDate, err2 := time.Parse(layout, endDateStr)
    if err1 != nil || err2 != nil {
        return c.Status(400).JSON(fiber.Map{"error": "Formato de data inválido. Use AAAA-MM-DD"})
    }

    daysDiff := int(endDate.Sub(startDate).Hours()/24) + 1
    prevEndDate := startDate.AddDate(0, 0, -1)
    prevStartDate := prevEndDate.AddDate(0, 0, -(daysDiff - 1))

    type MetricRow struct {
        Spend   float64
        Revenue float64
        Clicks  int
    }

    fetchData := func(start, end time.Time) (MetricRow, MetricRow, []float64) {
        var meta, google MetricRow
        sStr, eStr := start.Format(layout), end.Format(layout)

        database.DB.Table("fb_campaign_insights").
            Select("COALESCE(SUM(spend), 0), COALESCE(SUM(revenue), 0), COALESCE(SUM(clicks), 0)").
            Where("data BETWEEN ? AND ?", sStr, eStr).Row().Scan(&meta.Spend, &meta.Revenue, &meta.Clicks)
        
        database.DB.Table("google_campaign_insights").
            Select("COALESCE(SUM(spend), 0), COALESCE(SUM(revenue), 0), COALESCE(SUM(clicks), 0)").
            Where("data BETWEEN ? AND ?", sStr, eStr).Row().Scan(&google.Spend, &google.Revenue, &google.Clicks)

        var series []float64
        for i := 0; i < daysDiff; i++ {
            day := start.AddDate(0, 0, i).Format(layout)
            var dailyRev float64
            database.DB.Raw("SELECT (SELECT COALESCE(SUM(revenue), 0) FROM fb_campaign_insights WHERE data = ?) + (SELECT COALESCE(SUM(revenue), 0) FROM google_campaign_insights WHERE data = ?)", day, day).Scan(&dailyRev)
            series = append(series, dailyRev)
        }
        return meta, google, series
    }

    currMeta, currGoogle, currSeries := fetchData(startDate, endDate)
    prevMeta, prevGoogle, prevSeries := fetchData(prevStartDate, prevEndDate)

    currTotal := MetricRow{Spend: currMeta.Spend + currGoogle.Spend, Revenue: currMeta.Revenue + currGoogle.Revenue, Clicks: currMeta.Clicks + currGoogle.Clicks}
    prevTotal := MetricRow{Spend: prevMeta.Spend + prevGoogle.Spend, Revenue: prevMeta.Revenue + prevGoogle.Revenue, Clicks: prevMeta.Clicks + prevGoogle.Clicks}

    calcDelta := func(c, p float64) float64 {
        if p <= 0 { return 100.0 }
        return math.Round(((c-p)/p)*100)
    }

    calcROAS := func(rev, spend float64) float64 {
        if spend <= 0 { return 0 }
        return math.Round((rev/spend)*100) / 100
    }

    return c.JSON(fiber.Map{
        "status": "sucesso",
        "period_current":  fiber.Map{"start": startDateStr, "end": endDateStr},
        "period_previous": fiber.Map{"start": prevStartDate.Format(layout), "end": prevEndDate.Format(layout)},
        "stats": fiber.Map{
            "revenue": fiber.Map{"current": currTotal.Revenue, "prev": prevTotal.Revenue, "delta": calcDelta(currTotal.Revenue, prevTotal.Revenue)},
            "spend":   fiber.Map{"current": currTotal.Spend, "prev": prevTotal.Spend, "delta": calcDelta(currTotal.Spend, prevTotal.Spend)},
            "roas":    fiber.Map{"current": calcROAS(currTotal.Revenue, currTotal.Spend), "prev": calcROAS(prevTotal.Revenue, prevTotal.Spend), "delta": calcDelta(calcROAS(currTotal.Revenue, currTotal.Spend), calcROAS(prevTotal.Revenue, prevTotal.Spend))},
            "clicks":  fiber.Map{"current": currTotal.Clicks, "prev": prevTotal.Clicks, "delta": calcDelta(float64(currTotal.Clicks), float64(prevTotal.Clicks))},
        },
        "platforms": []fiber.Map{
            {"name": "Meta Ads", "revenue": currMeta.Revenue, "roas": calcROAS(currMeta.Revenue, currMeta.Spend)},
            {"name": "Google Ads", "revenue": currGoogle.Revenue, "roas": calcROAS(currGoogle.Revenue, currGoogle.Spend)},
        },
        "chart_data": fiber.Map{
            "labels":   generateLabels(daysDiff), // 🟢 AGORA ELA EXISTE
            "current":  currSeries,
            "previous": prevSeries,
        },
    })
}

// 🟢 FUNÇÃO QUE FALTAVA:
func generateLabels(n int) []string {
    labels := make([]string, n)
    for i := 0; i < n; i++ {
        labels[i] = "Dia " + time.Now().AddDate(0, 0, i-n+1).Format("02/01")
    }
    return labels
}