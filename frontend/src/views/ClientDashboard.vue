<script setup>
import { ref, onMounted, computed, watch } from "vue";
import api from "../services/api";
import KpiGrid from "../components/KpiGrid.vue";
import RevenueChart from "../components/RevenueChart.vue";
import CampaignRanking from "../components/CampaignRanking.vue";

const loading = ref(false);
const loadingSync = ref(false);
const analyticsData = ref(null);
const chartKey = ref(0);

// Datas padrão: Mês de Março de 2026
const startDate = ref("2026-03-01");
const endDate = ref("2026-03-31");

const fetchData = async () => {
  if (loading.value) return;

  loading.value = true;
  analyticsData.value = null; // Limpa a tela para o loading skeleton aparecer

  try {
    const response = await api.get("/analytics/dashboard", {
      params: {
        start_date: startDate.value,
        end_date: endDate.value,
      },
    });

    if (response.data && response.data.status === "sucesso") {
      analyticsData.value = response.data;
      chartKey.value++;
      console.log("✅ Números Atualizados:", response.data.consolidado);
    }
  } catch (error) {
    console.error("❌ Erro no fetch:", error);
  } finally {
    loading.value = false;
  }
};

const forceSync = async () => {
  loadingSync.value = true;
  try {
    await api.post("/sync/meta/history");
    await api.post("/sync/google/history");
    await fetchData();
    alert("✅ Tratores rodaram! Banco de dados 100% atualizado!");
  } catch (e) {
    console.error("❌ Erro no sync manual", e);
    alert("❌ Falha na comunicação com as APIs");
  } finally {
    loadingSync.value = false;
  }
};

// 🎯 Mapeamento Inteligente pegando do "consolidado" do Go
const dynamicStats = computed(() => {
  const k = analyticsData.value?.consolidado || {};
  return {
    total_revenue: k.total_revenue || 0,
    total_spend: k.total_spend || 0,
    total_roas: k.roas || 0,
    total_clicks: k.total_clicks || 0,
    total_impressions: k.total_impressions || 0,
  };
});

const chartDataMapped = computed(() => {
  const history = analyticsData.value?.chart_series || {};
  const labels = Object.keys(history).sort();

  return {
    labels: labels,
    datasets: [
      {
        label: "Meta Ads",
        data: labels.map((date) => history[date].meta || 0),
        borderColor: "#1877F2", // Azul Meta
        backgroundColor: "rgba(24, 119, 242, 0.1)",
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointRadius: 0,
      },
      {
        label: "Google Ads",
        data: labels.map((date) => history[date].google || 0),
        borderColor: "#C5A059", // Dourado Bracci
        backgroundColor: "rgba(197, 160, 89, 0.1)",
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointRadius: 0,
      },
    ],
  };
});

// Auto-update ao mudar datas
watch([startDate, endDate], fetchData);

onMounted(fetchData);
</script>

<template>
  <div class="space-y-12 animate-fade-in p-10 bg-[#FAFAFA] min-h-screen">
    <div
      class="bg-bracci-gold/5 border-l-2 border-bracci-gold p-6 flex justify-between items-center backdrop-blur-md"
    >
      <div class="flex items-center gap-4">
        <div
          class="w-1.5 h-1.5 bg-bracci-gold rounded-full animate-pulse"
        ></div>
        <p
          class="text-[9px] font-black uppercase tracking-[0.4em] text-bracci-gold"
        >
          Omnichannel Intelligence Protocol — v3.0 Powered by Golang
        </p>
      </div>
      <div class="text-[8px] font-mono text-gray-300 uppercase tracking-widest">
        Database History: 2023-2026 Online
      </div>
    </div>

    <header
      class="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-10"
    >
      <div class="space-y-4">
        <h2
          class="text-7xl font-extralight tracking-tighter uppercase text-black"
        >
          Performance
          <span class="font-black text-bracci-gold italic">Studio</span>
        </h2>
        <div class="h-1 w-24 bg-black"></div>
      </div>

      <div
        class="flex items-center gap-4 bg-white border border-gray-100 shadow-2xl p-1 rounded-sm"
      >
        <div class="px-6 py-3 flex flex-col border-r border-gray-50">
          <label
            class="text-[7px] font-black uppercase text-gray-400 tracking-[0.2em] mb-1"
            >Período Inicial</label
          >
          <input
            type="date"
            v-model="startDate"
            class="text-xs font-bold outline-none bg-transparent"
          />
        </div>
        <div class="px-6 py-3 flex flex-col border-r border-gray-50">
          <label
            class="text-[7px] font-black uppercase text-gray-400 tracking-[0.2em] mb-1"
            >Período Final</label
          >
          <input
            type="date"
            v-model="endDate"
            class="text-xs font-bold outline-none bg-transparent"
          />
        </div>
        <button
          @click="forceSync"
          :disabled="loadingSync"
          class="bg-black text-white px-8 py-6 text-[9px] font-black uppercase tracking-[0.2em] hover:bg-bracci-gold transition-all active:scale-95 disabled:opacity-50"
        >
          <span v-if="loadingSync" class="inline-block animate-spin mr-2"
            >🌀</span
          >
          {{ loadingSync ? "Syncing..." : "🔄 Atualizar APIs" }}
        </button>
      </div>
    </header>

    <KpiGrid v-if="analyticsData" :stats="dynamicStats" :kpis="dynamicStats" />

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-12">
      <div
        class="xl:col-span-2 bg-black p-12 shadow-2xl relative min-h-[600px] border border-white/5 rounded-sm"
      >
        <div class="flex justify-between items-center mb-10">
          <h3
            class="text-[10px] font-black uppercase tracking-[0.5em] text-gray-500 italic"
          >
            Omnichannel Growth
          </h3>
          <div class="flex gap-6">
            <div class="flex items-center gap-2">
              <div class="w-3 h-0.5 bg-[#1877F2]"></div>
              <span
                class="text-[8px] text-white font-bold uppercase tracking-widest"
                >Meta Ads</span
              >
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-0.5 bg-[#C5A059]"></div>
              <span
                class="text-[8px] text-white font-bold uppercase tracking-widest"
                >Google Ads</span
              >
            </div>
          </div>
        </div>

        <div class="relative h-[450px] overflow-hidden">
          <RevenueChart
            v-if="analyticsData"
            :key="chartKey"
            :chartData="chartDataMapped"
          />
        </div>
      </div>

      <div class="space-y-12">
        <div
          class="bg-white p-10 border border-gray-100 shadow-xl relative overflow-hidden group rounded-sm"
        >
          <h3
            class="text-[10px] font-black uppercase tracking-[0.5em] text-gray-300 mb-8 italic"
          >
            Data Snapshot
          </h3>
          <div class="space-y-8" v-if="analyticsData">
            <div class="flex items-start gap-5">
              <div class="w-1.5 h-1.5 bg-bracci-gold rounded-full mt-2"></div>
              <p
                class="text-[11px] text-gray-500 leading-relaxed uppercase tracking-wider font-bold"
              >
                Receita no Período:
                <span class="text-black font-black"
                  >R$
                  {{
                    dynamicStats.total_revenue.toLocaleString("pt-BR", {
                      minimumFractionDigits: 2,
                    })
                  }}</span
                >
              </p>
            </div>
            <div class="flex items-start gap-5">
              <div class="w-1.5 h-1.5 bg-black rounded-full mt-2"></div>
              <p
                class="text-[11px] text-gray-500 leading-relaxed uppercase tracking-wider font-bold"
              >
                Eficiência ROAS:
                <span class="text-bracci-gold font-black"
                  >{{ dynamicStats.total_roas.toFixed(2) }}x</span
                >.
              </p>
            </div>
          </div>
        </div>

        <CampaignRanking v-if="analyticsData" :stats="analyticsData" />
      </div>
    </div>
  </div>
</template>
