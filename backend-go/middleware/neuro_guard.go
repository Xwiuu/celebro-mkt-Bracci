package middleware

import (
	"fmt"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
)

func NeuroGuard() fiber.Handler {
	return func(c *fiber.Ctx) error {
		clientIP := c.IP()
		path := c.Path() // 👈 Pega o caminho da URL que está sendo acessada
		authorizedIP := os.Getenv("MY_AUTHORIZED_IP")
		currentTime := time.Now().Format("2006-01-02 15:04:05")

		// Log ultra detalhado para você não ter dúvida
		fmt.Printf("[%s] 🛡️ Verificando Escudo no caminho: %s | IP: %s\n", currentTime, path, clientIP)

		if clientIP == "127.0.0.1" || clientIP == "::1" || clientIP == authorizedIP {
			fmt.Printf("✅ ACESSO PERMITIDO para o Mestre em: %s\n", path)
			return c.Next()
		}

		fmt.Printf("❌ BLOQUEADO: Tentativa externa no caminho: %s | IP: %s\n", path, clientIP)
		return c.Status(fiber.StatusForbidden).JSON(fiber.Map{
			"message": "Protocolo NeuroGuard: Acesso Restrito.",
			"status":  "forbidden",
		})
	}
}