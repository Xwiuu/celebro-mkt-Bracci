<script setup>
import { ref, onMounted, watch } from "vue";
import VueApexCharts from "vue3-apexcharts";
// import api from "../services/api";

const startDate = ref("2026-03-15");
const endDate = ref("2026-03-31");
const loading = ref(false);
const report = ref(null);

// Configuração do Gráfico (Período x Período)
const chartOptions = ref({
  chart: { type: 'area', fontFamily: 'Inter, sans-serif', toolbar: { show: false }, zoom: { enabled: false } },
  colors: ['#D4AF37', '#e5e7eb'], // Bracci Gold e Cinza para o anterior
  fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0, stops: [0, 100] } },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 3 },
  xaxis: { categories: [], labels: { style: { colors: '#9ca3af', fontSize: '10px', fontWeight: 600 } }, axisBorder: { show: false }, axisTicks: { show: false } },
  yaxis: { labels: { formatter: (value) => `R$ ${(value / 1000).toFixed(0)}k`, style: { colors: '#9ca3af', fontSize: '10px', fontWeight: 600 } } },
  grid: { borderColor: '#f3f4f6', strokeDashArray: 4, xaxis: { lines: { show: true } }, yaxis: { lines: { show: true } } },
  legend: { position: 'top', horizontalAlign: 'right', fontSize: '12px', fontWeight: 700, markers: { radius: 12 } },
  tooltip: { theme: 'light', y: { formatter: (val) => formatBRL(val) } }
});

const chartSeries = ref([]);

const fetchComparative = async () => {
  loading.value = true;
  report.value = null; 
  
  try {
    // Simulando delay da API
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Mock robusto com as novas features
    const data = {
      period_current: { start: startDate.value, end: endDate.value },
      period_previous: { start: "2026-02-26", end: "2026-03-14" },
      stats: {
        "Cliques": { current: 249643, delta: -61.98, prev: 656558 },
        "Faturamento": { current: 1108319.72, delta: 3598.36, prev: 29967.84 },
        "Investimento": { current: 78922.43, delta: -24.01, prev: 103859.69 },
        "ROAS": { current: 14.04, delta: 4741.38, prev: 0.29 }
      },
      platforms: [
        { name: "Meta Ads", roas: 16.5, fat: 850000.50, inv: 51515.15, share: 76.7 },
        { name: "Google Ads", roas: 9.4, fat: 258319.22, inv: 27407.28, share: 23.3 }
      ],
      chart_data: {
        categories: ["Dia 1", "Dia 3", "Dia 6", "Dia 9", "Dia 12", "Dia 15"],
        current: [15000, 45000, 120000, 380000, 850000, 1108319],
        previous: [2000, 4500, 8000, 15000, 22000, 29967]
      }
    };

    report.value = data;
    
    // Atualiza o gráfico com os dados da API
    chartOptions.value = { ...chartOptions.value, xaxis: { ...chartOptions.value.xaxis, categories: data.chart_data.categories } };
    chartSeries.value = [
      { name: 'Período Atual', data: data.chart_data.current },
      { name: 'Período Anterior', data: data.chart_data.previous }
    ];

  } catch (e) {
    console.error("Erro na análise delta:", e);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchComparative);
watch([startDate, endDate], fetchComparative);

const formatValue = (label, value) => {
  if (label.includes('Cliques')) return Math.round(value).toLocaleString('pt-BR');
  if (label.includes('ROAS')) return value.toFixed(2);
  return formatBRL(value);
};

const formatBRL = (v) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
</script>

<template>
  <div class="min-h-screen bg-neutral-50 p-8 md:p-12 font-sans selection:bg-bracci-gold selection:text-white">
    <div class="max-w-[1600px] mx-auto space-y-12">
      
      <header class="flex flex-col md:flex-row md:justify-between md:items-end gap-6 border-b border-neutral-200 pb-8">
        <div>
          <div class="flex items-center gap-3 mb-2">
            <div class="w-2 h-2 rounded-full bg-bracci-gold animate-pulse"></div>
            <p class="text-[10px] font-black uppercase tracking-[0.3em] text-neutral-400">Omnichannel Dataset</p>
          </div>
          <h1 class="text-5xl md:text-6xl font-black tracking-tighter uppercase">
            Delta <span class="text-bracci-gold italic">Analysis</span>
          </h1>
        </div>
        
        <div class="flex items-center bg-white p-1 shadow-lg shadow-black/5 rounded-md border border-neutral-100 ring-1 ring-black/5">
          <div class="flex flex-col px-5 py-2 hover:bg-neutral-50 transition-colors rounded-l-md cursor-pointer">
            <span class="text-[9px] font-bold text-neutral-400 uppercase tracking-wider mb-1">Início</span>
            <input type="date" v-model="startDate" class="text-sm font-bold text-neutral-800 bg-transparent outline-none cursor-pointer" />
          </div>
          <div class="h-10 w-[1px] bg-neutral-100"></div>
          <div class="flex flex-col px-5 py-2 hover:bg-neutral-50 transition-colors rounded-r-md cursor-pointer">
            <span class="text-[9px] font-bold text-neutral-400 uppercase tracking-wider mb-1">Fim</span>
            <input type="date" v-model="endDate" class="text-sm font-bold text-neutral-800 bg-transparent outline-none cursor-pointer" />
          </div>
        </div>
      </header>

      <div v-if="loading" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="i in 4" :key="i" class="bg-white border border-neutral-100 rounded-sm h-[180px] animate-pulse"></div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 bg-white border border-neutral-100 rounded-sm h-[400px] animate-pulse"></div>
          <div class="bg-white border border-neutral-100 rounded-sm h-[400px] animate-pulse"></div>
        </div>
      </div>

      <TransitionGroup name="fade" tag="div" v-if="report && !loading" class="space-y-6">
        
        <div key="cards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="(data, label) in report.stats" :key="label" 
            class="bg-white p-8 border border-neutral-100 shadow-sm hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 group relative overflow-hidden rounded-sm"
          >
            <div :class="data.delta >= 0 ? 'bg-emerald-500' : 'bg-rose-500'" class="absolute top-0 left-0 w-full h-1 opacity-80 group-hover:opacity-100 transition-opacity"></div>
            <h4 class="text-[10px] font-black uppercase tracking-widest text-neutral-400 mb-6 flex items-center justify-between">
              {{ label }}
            </h4>
            <div class="space-y-1">
              <h2 class="text-3xl md:text-4xl font-black text-neutral-900 tracking-tighter">{{ formatValue(label, data.current) }}</h2>
              <p class="text-[11px] font-bold text-neutral-400 uppercase">Anterior: <span class="text-neutral-500">{{ formatValue(label, data.prev) }}</span></p>
            </div>
            <div class="mt-8 flex items-center gap-3 border-t border-neutral-50 pt-4">
              <span :class="data.delta >= 0 ? 'text-emerald-700 bg-emerald-50 ring-emerald-100' : 'text-rose-700 bg-rose-50 ring-rose-100'" 
                    class="text-[12px] font-black px-2.5 py-1 rounded-sm ring-1 flex items-center gap-1">
                {{ data.delta >= 0 ? '↗' : '↘' }} {{ Math.abs(data.delta) }}%
              </span>
            </div>
          </div>
        </div>

        <div key="charts" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          <div class="lg:col-span-2 bg-white p-8 border border-neutral-100 shadow-sm rounded-sm relative">
            <h3 class="text-sm font-black uppercase tracking-widest text-neutral-800 mb-2">Evolução de Faturamento</h3>
            <p class="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mb-8">Curva de aceleração vs Período Anterior</p>
            
            <div class="h-[300px] w-full">
              <VueApexCharts type="area" height="100%" :options="chartOptions" :series="chartSeries" />
            </div>
          </div>

          <div class="bg-white p-8 border border-neutral-100 shadow-sm rounded-sm flex flex-col">
            <h3 class="text-sm font-black uppercase tracking-widest text-neutral-800 mb-2">Plataformas</h3>
            <p class="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mb-8">Distribuição de Receita e ROAS</p>
            
            <div class="space-y-6 flex-1 flex flex-col justify-center">
              <div v-for="plat in report.platforms" :key="plat.name" class="group">
                <div class="flex justify-between items-end mb-2">
                  <div>
                    <h4 class="text-xs font-black uppercase text-neutral-900">{{ plat.name }}</h4>
                    <span class="text-[10px] font-bold text-neutral-400">ROAS {{ plat.roas.toFixed(2) }}x</span>
                  </div>
                  <div class="text-right">
                    <h4 class="text-sm font-black text-neutral-900">{{ formatBRL(plat.fat) }}</h4>
                    <span class="text-[10px] font-bold text-bracci-gold uppercase">{{ plat.share }}% Share</span>
                  </div>
                </div>
                <div class="w-full bg-neutral-100 h-2 rounded-full overflow-hidden">
                  <div class="bg-neutral-900 h-full rounded-full transition-all duration-1000" :style="`width: ${plat.share}%`"></div>
                </div>
              </div>
            </div>
          </div>

        </div>

      </TransitionGroup>

      <footer v-if="report && !loading" class="bg-neutral-900 text-white p-6 md:px-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 rounded-md shadow-2xl mt-12">
        <div class="flex flex-wrap gap-8 md:gap-12">
          <div class="flex flex-col gap-1">
            <span class="text-[9px] text-neutral-500 uppercase font-black tracking-widest">Período Selecionado</span>
            <span class="text-xs font-bold text-neutral-100">{{ report.period_current.start }} a {{ report.period_current.end }}</span>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-[9px] text-neutral-500 uppercase font-black tracking-widest">Base de Comparação</span>
            <span class="text-xs font-bold text-bracci-gold">{{ report.period_previous.start }} a {{ report.period_previous.end }}</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
          <span class="text-[10px] font-mono text-neutral-500 uppercase tracking-widest">Sistema Operacional • Synxia Engine</span>
        </div>
      </footer>
      
    </div>
  </div>
</template>