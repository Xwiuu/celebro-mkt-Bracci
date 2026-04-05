package handlers

import (
	"backend-go/services"
	"github.com/gofiber/fiber/v2"
)

// Rota para o Sync de Todo Dia (Rápido, últimos 7 dias)
func TriggerMetaDailySync(c *fiber.Ctx) error {
	err := services.SyncMetaDaily()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"status": "erro", "message": err.Error()})
	}
	return c.JSON(fiber.Map{"status": "sucesso", "message": "Dados recentes importados com sucesso!"})
}

// Rota para o Sync de Histórico (Pesado, anos para trás)
func TriggerMetaHistorySync(c *fiber.Ctx) error {
	err := services.SyncMetaHistory()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"status": "erro", "message": err.Error()})
	}
	return c.JSON(fiber.Map{"status": "sucesso", "message": "Histórico massivo importado com sucesso!"})
}

// Rota para o Sync Diário Google
func TriggerGoogleDailySync(c *fiber.Ctx) error {
	err := services.SyncGoogleDaily()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"status": "erro", "message": err.Error()})
	}
	return c.JSON(fiber.Map{"status": "sucesso", "message": "Google: Dados recentes importados!"})
}

// Rota para o Sync Histórico Google
func TriggerGoogleHistorySync(c *fiber.Ctx) error {
	err := services.SyncGoogleHistory()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"status": "erro", "message": err.Error()})
	}
	return c.JSON(fiber.Map{"status": "sucesso", "message": "Google: Histórico massivo importado!"})
}