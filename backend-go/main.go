package main

import (
	"fmt"
	"log"

	"backend-go/database"
	"backend-go/handlers"
	"backend-go/middleware"
	"backend-go/models"
	"backend-go/services"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/joho/godotenv"
)

func main() {
	// 1. Carrega as chaves do .env
	err := godotenv.Load()
	if err != nil {
		log.Println("Aviso: Arquivo .env não encontrado. Usando variáveis do sistema.")
	}

	// 2. Conexão e Migração do Banco de Dados
	database.ConnectDB()
	fmt.Println("⚙️ Sincronizando models com o Postgres...")

	// ADICIONE O MODELO DO GOOGLE AQUI DENTRO
	err = database.DB.AutoMigrate(
		&models.CampaignInsight{},
		&models.GoogleCampaignInsight{}, // Certifique-se que esse nome existe no seu models/
	)
	if err != nil {
		log.Fatal("❌ Erro na migração: ", err)
	}

	// 3. Inicia o Cron do Relógio Suíço (Sync Diário às 03:00 AM)
	services.InitScheduler()

	// 4. Configuração do Servidor Fiber
	app := fiber.New()

	// Liberação de CORS (Essencial para o Vue.js acessar o Go)
	app.Use(cors.New(cors.Config{
		AllowOrigins: "*",
		AllowHeaders: "Origin, Content-Type, Accept",
	}))

	// ============================================================
	// 🌍 GRUPO 1: ROTAS PÚBLICAS (Dashboard e Analytics)
	// Estas rotas o pessoal da agência pode ver normalmente.
	// ============================================================
	api := app.Group("/api/v1")

	// Dashboard de KPIs e Relatórios
	api.Get("/analytics/dashboard", handlers.GetMarketingPerformance)
	api.Get("/analytics/comparative", handlers.GetComparativeAnalysis)
	
	// Triggers Manuais de Sincronização (Botão de Refresh)
	api.Post("/sync/meta/daily", handlers.TriggerMetaDailySync)
	api.Post("/sync/meta/history", handlers.TriggerMetaHistorySync)
	api.Post("/sync/google/daily", handlers.TriggerGoogleDailySync)
	api.Post("/sync/google/history", handlers.TriggerGoogleHistorySync)

	// ============================================================
	// 🔒 GRUPO 2: PROTOCOLO NEURO-SÓCIO (BLINDADO POR IP)
	// Apenas você (Localhost ou IP do .env) consegue enxergar aqui.
	// ============================================================
	neuro := api.Group("/neuro-socio", middleware.NeuroGuard())

	// Validação de Acesso (Usado pelo Frontend para esconder o botão)
	neuro.Get("/status", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{
			"can_access": true,
			"message":    "Identidade confirmada. Bem-vindo, Mestre.",
		})
	})

	// Motor de Análise IA (Onde o Python vai rodar)
	neuro.Get("/analyze", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{"message": "Cérebro IA pronto para análise estatística."})
	})

	// ============================================================

	log.Println("🚀 Motor Go Rodando na Porta 8000!")
	log.Fatal(app.Listen(":8000"))
}