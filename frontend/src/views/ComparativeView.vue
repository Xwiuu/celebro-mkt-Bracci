<script setup>
import { ref, onMounted, watch } from "vue";
import VueApexCharts from "vue3-apexcharts";
import CountUp from 'vue-countup-v3'; // 📦 Novo: Contadores animados
import { startOfMonth, subDays, format } from 'date-fns'; // 📦 Novo: Cálculos de data

import api from "../services/api";

const startDate = ref("2026-03-01");
const endDate = ref("2026-03-31");
const loading = ref(false);
const report = ref(null);
const currentRangeLabel = ref("Mês Atual"); // Para o feedback visual

// Função para mudar o período com um clique
const setRange = (range) => {
  const hoje = new Date();
  let start, end;

  switch (range) {
    case '7d':
      currentRangeLabel.value = "Últimos 7 Dias";
      end = subDays(hoje, 1); // Ontem
      start = subDays(end, 6); // 7 dias atrás
      break;
    case '30d':
      currentRangeLabel.value = "Últimos 30 Dias";
      end = subDays(hoje, 1);
      start = subDays(end, 29);
      break;
    case 'mes':
      currentRangeLabel.value = "Mês Atual";
      start = startOfMonth(hoje);
      end = hoje;
      break;
  }

  startDate.value = format(start, 'yyyy-MM-dd');
  endDate.value = format(end, 'yyyy-MM-dd');
};

// Configuração do Gráfico (Ajustado Tooltip e Linhas)
const chartOptions = ref({
  chart: { type: 'area', fontFamily: 'Inter, sans-serif', toolbar: { show: false }, zoom: { enabled: false } },
  colors: ['#D4AF37', '#e5e7eb'], 
  fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.5, opacityTo: 0, stops: [0, 100] } },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 3 },
  xaxis: { categories: [], labels: { style: { colors: '#9ca3af', fontSize: '10px', fontWeight: 600 } }, axisBorder: { show: false }, axisTicks: { show: false } },
  yaxis: { labels: { formatter: (value) => `R$ ${(value / 1000).toFixed(0)}k`, style: { colors: '#9ca3af', fontSize: '10px', fontWeight: 600 } } },
  grid: { borderColor: '#f3f4f6', strokeDashArray: 4, xaxis: { lines: { show: true } }, yaxis: { lines: { show: true } } },
  legend: { position: 'top', horizontalAlign: 'right', fontSize: '12px', fontWeight: 700, markers: { radius: 12 } },
  tooltip: { 
    theme: 'light', 
    y: { formatter: (val) => formatBRL(val) },
    style: { fontSize: '12px', fontFamily: 'Inter, sans-serif' },
    marker: { show: true },
    x: { show: true },
    items: { display: 'flex' }
  }
});

const chartSeries = ref([]);

const fetchComparative = async () => {
  loading.value = true;
  report.value = null;

  try {
    // 🟢 CHAMADA REAL PARA O BACKEND
    const response = await api.get("/analytics/comparative", {
      params: {
        start_date: startDate.value,
        end_date: endDate.value
      }
    });

    const backendData = response.data;

    report.value = {
      ...backendData,
      stats: {
        "Captado Real": backendData.stats.revenue,
        "Total Gasto": backendData.stats.spend,
        "ROAS Global": backendData.stats.roas,
        "Volume Cliques": backendData.stats.clicks
      }
    };

    chartOptions.value = {
      ...chartOptions.value,
      xaxis: { ...chartOptions.value.xaxis, categories: backendData.chart_data.labels }
    };

    chartSeries.value = [
      { name: 'Período Atual', data: backendData.chart_data.current },
      { name: 'Período Anterior', data: backendData.chart_data.previous }
    ];

  } catch (e) {
    console.error("Erro na análise real:", e);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchComparative);
watch([startDate, endDate], fetchComparative);

const formatBRL = (v) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
</script>

<template>
  <div class="min-h-screen bg-[#FAFAFA] p-8 md:p-12 font-sans selection:bg-bracci-gold selection:text-white">
    <div class="max-w-[1600px] mx-auto space-y-12 transition-all duration-500">
      
      <header class="flex flex-col lg:flex-row lg:justify-between lg:items-end gap-10 border-b border-gray-100 pb-12">
        <div>
          <div class="flex items-center gap-3 mb-2">
            <div class="w-1.5 h-1.5 rounded-full bg-bracci-gold animate-pulse"></div>
            <p class="text-[9px] font-black uppercase tracking-[0.4em] text-gray-400">Omnichannel Intelligence Protocol — v3.0</p>
          </div>
          <h1 class="text-6xl md:text-7xl font-extralight tracking-tighter uppercase text-black">
            Delta <span class="text-bracci-gold font-black italic">Analysis</span>
          </h1>
        </div>
        
        <div class="flex flex-col sm:flex-row items-center gap-6">
          <div class="flex gap-2 bg-white/50 backdrop-blur-sm p-1.5 rounded-full border border-gray-100 shadow-inner">
            <button @click="setRange('mes')" :class="currentRangeLabel === 'Mês Atual' ? 'bg-black text-white' : 'hover:bg-gray-100'" class="px-5 py-3 rounded-full text-[9px] font-black uppercase tracking-[0.2em] transition-all">Mês Atual</button>
            <button @click="setRange('30d')" :class="currentRangeLabel === 'Últimos 30 Dias' ? 'bg-black text-white' : 'hover:bg-gray-100'" class="px-5 py-3 rounded-full text-[9px] font-black uppercase tracking-[0.2em] transition-all">Últimos 30d</button>
            <button @click="setRange('7d')" :class="currentRangeLabel === 'Últimos 7 Dias' ? 'bg-black text-white' : 'hover:bg-gray-100'" class="px-5 py-3 rounded-full text-[9px] font-black uppercase tracking-[0.2em] transition-all">Últimos 7d</button>
          </div>

          <div class="flex items-center bg-white/80 backdrop-blur-lg p-1 shadow-2xl shadow-black/5 rounded-sm border border-gray-100 ring-1 ring-black/5">
            <div class="flex flex-col px-6 py-3 hover:bg-neutral-50 transition-colors rounded-l-sm cursor-pointer border-r border-gray-100">
              <span class="text-[7px] font-black text-gray-400 uppercase tracking-[0.2em] mb-1">Inicial</span>
              <input type="date" v-model="startDate" class="text-xs font-bold text-neutral-800 bg-transparent outline-none cursor-pointer" />
            </div>
            <div class="flex flex-col px-6 py-3 hover:bg-neutral-50 transition-colors rounded-r-sm cursor-pointer">
              <span class="text-[7px] font-black text-gray-400 uppercase tracking-[0.2em] mb-1">Final</span>
              <input type="date" v-model="endDate" class="text-xs font-bold text-neutral-800 bg-transparent outline-none cursor-pointer" />
            </div>
          </div>
        </div>
      </header>

      <div v-if="loading" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="i in 4" :key="i" class="bg-white border border-gray-100 rounded-sm h-[200px] animate-pulse"></div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 bg-white border border-gray-100 rounded-sm h-[400px] animate-pulse"></div>
          <div class="bg-white border border-gray-100 rounded-sm h-[400px] animate-pulse"></div>
        </div>
      </div>

      <TransitionGroup name="fade" tag="div" v-if="report && !loading" class="space-y-8">
        
        <div key="cards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="(data, label) in report.stats" :key="label" 
            class="bg-white/90 backdrop-blur-xl p-9 border border-gray-100 shadow-xl shadow-black/5 hover:shadow-bracci-gold/10 hover:border-bracci-gold hover:-translate-y-1 transition-all duration-300 group relative overflow-hidden rounded-sm"
          >
            <div :class="data.delta >= 0 ? 'bg-emerald-500' : 'bg-rose-500'" class="absolute top-0 left-0 w-full h-1 opacity-60 group-hover:opacity-100 transition-opacity"></div>
            
            <h4 class="text-[10px] font-black uppercase tracking-[0.3em] text-gray-400 mb-8 flex items-center justify-between">
              {{ label }}
            </h4>
            
            <div class="space-y-1.5">
              <h2 class="text-5xl font-black text-black tracking-tighter">
                <span v-if="label.includes('Captado') || label.includes('Total Gasto')">R$ </span>
                <CountUp :end-val="data.current" :options="{ decimalPlaces: (label.includes('ROAS') ? 2 : 0), useEasing: true, separator: '.' }"></CountUp>
                <span v-if="label.includes('ROAS')">x</span>
              </h2>
              
              <p class="text-[11px] font-bold text-gray-400 uppercase tracking-wide">
                Anterior: <span class="text-gray-500 font-mono">{{ formatBRL(data.prev) }}</span>
              </p>
            </div>
            
            <div class="mt-10 flex items-center gap-3 border-t border-gray-50 pt-5">
              <span :class="data.delta >= 0 ? 'text-emerald-800 bg-emerald-50 ring-emerald-100' : 'text-rose-800 bg-rose-50 ring-rose-100'" 
                    class="text-[11px] font-black px-3 py-1 rounded-sm ring-1 flex items-center gap-1.5 shadow-inner">
                {{ data.delta >= 0 ? '↗' : '↘' }} {{ Math.abs(data.delta).toFixed(1) }}%
              </span>
              <span class="text-[9px] text-gray-400 uppercase tracking-widest font-bold">vs Período Anterior</span>
            </div>
          </div>
        </div>

        <div key="charts" class="grid grid-cols-1 xl:grid-cols-3 gap-8">
          
          <div class="xl:col-span-2 bg-black p-12 shadow-2xl relative min-h-[500px] border border-white/5 rounded-sm overflow-hidden group">
            <div class="absolute -top-1/2 -left-1/4 w-full h-full bg-bracci-gold/10 rounded-full blur-[150px] transition-transform duration-1000 group-hover:scale-110"></div>
            
            <div class="relative z-10 space-y-2 mb-12">
              <h3 class="text-[10px] font-black uppercase tracking-[0.5em] text-gray-500 italic">Omnichannel Growth</h3>
              <h2 class="text-2xl font-black text-white tracking-tighter uppercase italic">Curva de aceleração vs Passado</h2>
            </div>
            
            <div class="relative z-10 h-[350px] w-full">
              <VueApexCharts type="area" height="100%" :options="chartOptions" :series="chartSeries" />
            </div>
          </div>

          <div class="bg-white/80 backdrop-blur-xl p-10 border border-gray-100 shadow-xl rounded-sm flex flex-col">
            <h3 class="text-sm font-black uppercase tracking-widest text-gray-800 mb-2">Plataformas</h3>
            <p class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-10">Distribuição de Receita e ROAS</p>
            
            <div class="space-y-8 flex-1 flex flex-col justify-center">
              <div v-for="plat in report.platforms" :key="plat.name" class="group relative">
                <div class="flex justify-between items-end mb-3">
                  <div>
                    <h4 class="text-xs font-black uppercase text-gray-900">{{ plat.name }}</h4>
                    <span class="text-[10px] font-bold text-gray-400">ROAS {{ plat.roas.toFixed(2) }}x</span>
                  </div>
                  <div class="text-right">
                    <h4 class="text-sm font-black text-black">{{ formatBRL(plat.fat) }}</h4>
                    <span class="text-[10px] font-black text-bracci-gold uppercase">{{ plat.share }}% Share</span>
                  </div>
                </div>
                <div class="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                  <div class="bg-gradient-to-r from-gray-900 to-black h-full rounded-full transition-all duration-1000 group-hover:from-bracci-gold group-hover:to-bracci-gold" :style="`width: ${plat.share}%`"></div>
                </div>
              </div>
            </div>
          </div>

        </div>

      </TransitionGroup>

      <footer v-if="report && !loading" class="bg-black text-white p-8 px-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 rounded-sm shadow-3xl mt-16 border border-white/5 relative overflow-hidden">
        <div class="absolute -top-1/2 left-0 w-full h-full bg-bracci-gold/5 blur-[100px]"></div>
        <div class="flex flex-wrap gap-8 md:gap-16 relative z-10">
          <div class="flex flex-col gap-1.5">
            <span class="text-[9px] text-gray-500 uppercase font-black tracking-widest">Janela Selecionada</span>
            <span class="text-xs font-bold text-white">{{ report.period_current.start }} <span class="text-gray-600">até</span> {{ report.period_current.end }}</span>
          </div>
          <div class="flex flex-col gap-1.5">
            <span class="text-[9px] text-gray-500 uppercase font-black tracking-widest">Base Comparativa</span>
            <span class="text-xs font-bold text-bracci-gold">{{ report.period_previous.start }} <span class="text-gray-700">até</span> {{ report.period_previous.end }}</span>
          </div>
        </div>
        <div class="flex items-center gap-2 relative z-10">
          <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
          <span class="text-[10px] font-mono text-gray-500 uppercase tracking-widest">Omnichannel Synxia Engine v3.0 // Online</span>
        </div>
      </footer>
      
    </div>
  </div>
</template>

<style scoped>
/* Transição Fade suave para TransitionGroup */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.5s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>