<script setup>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps({
  data: { type: Array, default: () => [] }
})

const chartData = {
  labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
  datasets: [
    {
      label: 'Receita (Bracci)',
      borderColor: '#C5A059',
      backgroundColor: 'rgba(197, 160, 89, 0.05)',
      fill: true,
      data: [12000, 15000, 11000, 18000, 22000, 25000, 28000],
      tension: 0.4
    },
    {
      label: 'Investimento',
      borderColor: '#1A1A1A',
      backgroundColor: 'transparent',
      borderDash: [5, 5],
      data: [2000, 2200, 2100, 2500, 2800, 3000, 3200],
      tension: 0.4
    }
  ]
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    y: { display: false },
    x: { grid: { display: false }, ticks: { font: { size: 10, family: 'Inter' }, color: '#4A4A4A' } }
  }
}
</script>

<template>
  <div class="h-[300px] w-full">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>
