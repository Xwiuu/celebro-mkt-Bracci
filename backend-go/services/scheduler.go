package services

import (
	"fmt"
	"github.com/robfig/cron/v3"
	"time"
)

func InitScheduler() {
	// Criamos um novo agendador com suporte a logs e fuso horário local
	c := cron.New(cron.WithLocation(time.Local))

	// 🎯 AGENDAMENTO: Todos os dias às 03:00 da manhã
	// A sintaxe é: "minuto hora dia_do_mês mês dia_da_semana"
	_, err := c.AddFunc("00 03 * * *", func() {
		fmt.Printf("[%s] 🕒 Relógio Suíço ativado! Iniciando sincronização diária...\n", time.Now().Format("15:04:05"))
		
		// Sincroniza Meta (últimos 7 dias para garantir que não escapa nada)
		errMeta := SyncMetaDaily()
		if errMeta != nil {
			fmt.Printf("❌ Erro automático Meta: %v\n", errMeta)
		} else {
			fmt.Println("✅ Meta: Sincronização automática concluída!")
		}

		// Sincroniza Google (últimos 7 dias)
		errGoogle := SyncGoogleDaily()
		if errGoogle != nil {
			fmt.Printf("❌ Erro automático Google: %v\n", errGoogle)
		} else {
			fmt.Println("✅ Google: Sincronização automática concluída!")
		}
		
		fmt.Printf("[%s] 🏁 Rotina de madrugada finalizada.\n", time.Now().Format("15:04:05"))
	})

	if err != nil {
		fmt.Printf("❌ Erro ao iniciar o Relógio Suíço: %v\n", err)
		return
	}

	// Inicia o agendador numa goroutine separada (não trava o servidor)
	c.Start()
	fmt.Println("⌚ Relógio Suíço configurado: Sincronização automática todos os dias às 03:00 AM.")
}