package main

import (
    "fmt"
    "log"

    "backend-go/database"
    "backend-go/handlers"
    "backend-go/models" // 👈 PRECISA IMPORTAR OS MODELS AQUI

    "github.com/gofiber/fiber/v2"
    "github.com/gofiber/fiber/v2/middleware/cors"
    "github.com/joho/godotenv"
)

func main() {
    err := godotenv.Load()
    if err != nil {
        log.Println("Aviso: Arquivo .env não encontrado. Usando variáveis do sistema.")
    }

    // Conecta no banco
    database.ConnectDB()

    // ✨ A MÁGICA ACONTECE AQUI ✨
    // O AutoMigrate vai olhar o model e CRIAR a coluna "spend", "revenue", etc no Postgres se elas não existirem!
    fmt.Println("⚙️ Sincronizando o banco de dados...")
    err = database.DB.AutoMigrate(&models.CampaignInsight{})
    if err != nil {
        log.Fatal("❌ Erro ao sincronizar o banco: ", err)
    }
    fmt.Println("✅ Banco de dados sincronizado com sucesso!")

    // 🕵️‍♂️ MÁQUINA DE RAIO-X: BORA VER AS TABELAS REAIS!
    var tables []string
    database.DB.Raw("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'").Scan(&tables)
    fmt.Println("========================================")
    fmt.Println("🗄️ TABELAS ENCONTRADAS NO BANCO:")
    for _, table := range tables {
        fmt.Println(" ➡️", table)
    }
    fmt.Println("========================================")

	app := fiber.New()
	// Libera o CORS pro Vue conseguir acessar
	app.Use(cors.New(cors.Config{
		AllowOrigins: "*",
		AllowHeaders: "Origin, Content-Type, Accept",
	}))

	// ROTAS DA API v1
	api := app.Group("/api/v1")
	api.Get("/dashboard/summary", handlers.GetDashboardSummary)
	api.Get("/dashboard/comparative", handlers.GetComparativeAnalysis)
	api.Post("/sync/meta", handlers.TriggerMetaSync)

	log.Println("🚀 Motor Go Rodando na Porta 8000!")
	log.Fatal(app.Listen(":8000"))
}