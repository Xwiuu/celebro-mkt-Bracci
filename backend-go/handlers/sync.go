package handlers

import (
	"backend-go/services"
	"github.com/gofiber/fiber/v2"
)

func TriggerMetaSync(c *fiber.Ctx) error {
	// Chama a nossa função de serviço
	err := services.SyncMetaCampaigns()
	
	if err != nil {
		return c.Status(500).JSON(fiber.Map{
			"status":  "erro",
			"message": err.Error(),
		})
	}

	return c.JSON(fiber.Map{
		"status":  "sucesso",
		"message": "Dados do Facebook importados com sucesso pro painel!",
	})
}