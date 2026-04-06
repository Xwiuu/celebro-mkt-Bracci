<script setup>
import { ref, onMounted, watch } from "vue";
import VueApexCharts from "vue3-apexcharts";
import CountUp from 'vue-countup-v3';
import { startOfMonth, subDays, format } from 'date-fns';
import api from "../services/api";

// 📅 Controle de Datas
const startDate = ref(format(startOfMonth(new Date()), 'yyyy-MM-dd'));
const endDate = ref(format(new Date(), 'yyyy-MM-dd'));
const loading = ref(false);
const report = ref(null);
const currentRangeLabel = ref("Mês Atual");

const setRange = (range) => {
  const hoje = new Date();
  let start, end;

  switch (range) {
    case '7d':
      currentRangeLabel.value = "Últimos 7 Dias";
      end = subDays(hoje, 1);
      start = subDays(end, 6);
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

// 📈 Configuração do Gráfico
const chartOptions = ref({
  chart: { type: 'area', fontFamily: 'Inter, sans-serif', toolbar: { show: false }, zoom: { enabled: false } },
  colors: ['#D4AF37', '#3f3f46'], 
  fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0, stops: [0, 100] } },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 3 },
  xaxis: { 
    categories: [], 
    labels: { style: { colors: '#9ca3af', fontSize: '10px', fontWeight: 600 } },
    axisBorder: { show: false },
    axisTicks: { show: false }
  },
  yaxis: { labels: { formatter: (value) => `R$ ${(value / 1000).toFixed(0)}k`, style: { colors: '#9ca3af', fontSize: '10px', fontWeight: 600 } } },
  grid: { borderColor: '#f3f4f6', strokeDashArray: 4 },
  legend: { position: 'top', horizontalAlign: 'right', labels: { colors: '#9ca3af' } },
  tooltip: { 
    theme: 'dark', 
    y: { formatter: (val) => formatBRL(val) }
  }
});

const chartSeries = ref([]);

// 🚀 Chamada Real para o Motor Go
const fetchComparative = async () => {
  loading.value = true;
  try {
    const response = await api.get("/analytics/comparative", {
      params: {
        start_date: startDate.value,
        end_date: endDate.value
      }
    });

    const b = response.data;

    // 🧠 Mapeamento: Transformando JSON do Go em labels para o Vue
    const totalRev = b.stats.revenue.current || 1;
    
    report.value = {
      period_current: b.period_current,
      period_previous: b.period_previous,
      stats: {
        "Captado Real": b.stats.revenue,
        "Total Gasto": b.stats.spend,
        "ROAS Global": b.stats.roas,
        "Volume Cliques": b.stats.clicks
      },
      platforms: b.platforms.map(p => ({
        name: p.name,
        roas: p.roas,
        fat: p.revenue,
        share: ((p.revenue / totalRev) * 100).toFixed(1)
      }))
    };

    // Atualiza o Gráfico
    chartOptions.value = { 
      ...chartOptions.value, 
      xaxis: { ...chartOptions.value.xaxis, categories: b.chart_data.labels } 
    };
    chartSeries.value = [
      { name: 'Período Atual', data: b.chart_data.current },
      { name: 'Período Anterior', data: b.chart_data.previous }
    ];

  } catch (e) {
    console.error("Erro na conexão com o Motor Go:", e);
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
    <div class="max-w-[1600px] mx-auto space-y-12">
      
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
            <button @click="setRange('mes')" :class="currentRangeLabel === 'Mês Atual' ? 'bg-black text-white shadow-lg' : 'hover:bg-gray-100'" class="px-5 py-3 rounded-full text-[9px] font-black uppercase tracking-[0.2em] transition-all">Mês Atual</button>
            <button @click="setRange('30d')" :class="currentRangeLabel === 'Últimos 30 Dias' ? 'bg-black text-white shadow-lg' : 'hover:bg-gray-100'" class="px-5 py-3 rounded-full text-[9px] font-black uppercase tracking-[0.2em] transition-all">Últimos 30d</button>
            <button @click="setRange('7d')" :class="currentRangeLabel === 'Últimos 7 Dias' ? 'bg-black text-white shadow-lg' : 'hover:bg-gray-100'" class="px-5 py-3 rounded-full text-[9px] font-black uppercase tracking-[0.2em] transition-all">Últimos 7d</button>
          </div>

          <div class="flex items-center bg-white shadow-2xl rounded-sm border border-gray-100">
            <div class="flex flex-col px-6 py-3 border-r border-gray-100">
              <span class="text-[7px] font-black text-gray-400 uppercase tracking-[0.2em] mb-1">Inicial</span>
              <input type="date" v-model="startDate" class="text-xs font-bold text-neutral-800 outline-none" />
            </div>
            <div class="flex flex-col px-6 py-3">
              <span class="text-[7px] font-black text-gray-400 uppercase tracking-[0.2em] mb-1">Final</span>
              <input type="date" v-model="endDate" class="text-xs font-bold text-neutral-800 outline-none" />
            </div>
          </div>
        </div>
      </header>

      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div v-for="i in 4" :key="i" class="bg-white border border-gray-100 rounded-sm h-[180px] animate-pulse"></div>
      </div>

      <TransitionGroup name="fade" tag="div" v-if="report && !loading" class="space-y-8">
        
        <div key="cards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="(data, label) in report.stats" :key="label" 
            class="bg-white p-9 border border-gray-100 shadow-xl hover:border-bracci-gold transition-all duration-300 group rounded-sm"
          >
            <h4 class="text-[10px] font-black uppercase tracking-[0.3em] text-gray-400 mb-8">{{ label }}</h4>
            
            <div class="space-y-1.5">
              <h2 class="text-5xl font-black text-black tracking-tighter">
                <span v-if="label.includes('Captado') || label.includes('Total Gasto')">R$ </span>
                <CountUp :end-val="data.current" :options="{ decimalPlaces: (label.includes('ROAS') ? 2 : 0), separator: '.' }"></CountUp>
                <span v-if="label.includes('ROAS')">x</span>
              </h2>
              <p class="text-[11px] font-bold text-gray-400 uppercase">
                Anterior: <span class="text-gray-500 font-mono">{{ formatBRL(data.prev) }}</span>
              </p>
            </div>
            
            <div class="mt-10 flex items-center gap-3 border-t border-gray-50 pt-5">
              <span :class="data.delta >= 0 ? 'text-emerald-800 bg-emerald-50' : 'text-rose-800 bg-rose-50'" 
                    class="text-[11px] font-black px-3 py-1 rounded-sm ring-1 ring-inset">
                {{ data.delta >= 0 ? '↗' : '↘' }} {{ Math.abs(data.delta) }}%
              </span>
              <span class="text-[9px] text-gray-400 uppercase tracking-widest font-bold">vs Período Anterior</span>
            </div>
          </div>
        </div>

        <div key="charts" class="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div class="xl:col-span-2 bg-black p-12 shadow-2xl rounded-sm relative overflow-hidden group">
            <div class="relative z-10 mb-12">
              <h3 class="text-[10px] font-black uppercase tracking-[0.5em] text-gray-500 italic">Omnichannel Growth</h3>
              <h2 class="text-2xl font-black text-white tracking-tighter uppercase italic">Curva de Faturamento</h2>
            </div>
            <div class="relative z-10 h-[350px]">
              <VueApexCharts type="area" height="100%" :options="chartOptions" :series="chartSeries" />
            </div>
          </div>

          <div class="bg-white p-10 border border-gray-100 shadow-xl rounded-sm">
            <h3 class="text-sm font-black uppercase tracking-widest text-gray-800 mb-10">Market Share</h3>
            <div class="space-y-10">
              <div v-for="plat in report.platforms" :key="plat.name">
                <div class="flex justify-between items-end mb-3">
                  <div>
                    <h4 class="text-xs font-black uppercase text-gray-900">{{ plat.name }}</h4>
                    <span class="text-[10px] font-bold text-gray-400">ROAS {{ plat.roas }}x</span>
                  </div>
                  <div class="text-right">
                    <h4 class="text-sm font-black text-black">{{ formatBRL(plat.fat) }}</h4>
                    <span class="text-[10px] font-black text-bracci-gold uppercase">{{ plat.share }}% Share</span>
                  </div>
                </div>
                <div class="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                  <div class="bg-black h-full transition-all duration-1000" :style="`width: ${plat.share}%`"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </TransitionGroup>

      <footer v-if="report && !loading" class="bg-black text-white p-10 flex flex-col md:flex-row justify-between items-center rounded-sm">
        <div class="flex gap-16">
          <div class="flex flex-col gap-1.5">
            <span class="text-[9px] text-gray-500 uppercase font-black tracking-widest">Janela Selecionada</span>
            <span class="text-xs font-bold">{{ report.period_current.start }} — {{ report.period_current.end }}</span>
          </div>
          <div class="flex flex-col gap-1.5">
            <span class="text-[9px] text-gray-500 uppercase font-black tracking-widest">Base Comparativa</span>
            <span class="text-xs font-bold text-bracci-gold">{{ report.period_previous.start }} — {{ report.period_previous.end }}</span>
          </div>
        </div>
        <span class="text-[10px] font-mono text-gray-500 uppercase tracking-widest mt-4 md:mt-0">Synxia Engine v3.0 // Online</span>
      </footer>
      
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: all 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(20px); }
</style>