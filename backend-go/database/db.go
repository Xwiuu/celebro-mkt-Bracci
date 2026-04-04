package database

import (
	"log"
	"os"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

func ConnectDB() {
	dsn := os.Getenv("DATABASE_URL")
	
	// Conecta no banco já existente
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info), // Mostra as queries no terminal pra gente ver a mágica
	})

	if err != nil {
		log.Fatal("❌ Falha ao conectar no banco de dados! Erro: \n", err)
	}

	log.Println("✅ Conectado ao Arquivo de Aço (Postgres) com Sucesso!")
	DB = db
}