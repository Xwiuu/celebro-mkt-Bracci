<script setup>
import { ref, watch } from 'vue';
import { DatePicker } from 'v-calendar';
import 'v-calendar/dist/style.css';

// TAREFA: Garantir que o range comece com objetos de data válidos
const range = ref({
  start: new Date(new Date().setDate(new Date().getDate() - 30)),
  end: new Date()
});

const emit = defineEmits(['change']);
const isOpen = ref(false);

const setPreset = (days) => {
  const end = new Date();
  const start = new Date();
  start.setDate(end.getDate() - days);
  range.value = { start, end };
};

const formatDate = (date) => {
  if (!date) return '...';
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' });
};

// TAREFA: Watcher simplificado e seguro para emitir o novo range
watch(range, (newRange) => {
  if (newRange && newRange.start && newRange.end) {
    emit('change', newRange);
  }
}, { deep: true });
</script>

<template>
  <div class="relative font-sans">
    <!-- Luxury Input Trigger -->
    <button 
      @click="isOpen = !isOpen"
      class="bg-white border-thin border-gray-100 px-8 py-3 flex items-center gap-6 shadow-sm hover:shadow-md transition-all group"
    >
      <div class="flex flex-col text-left">
        <span class="text-[8px] text-gray-300 font-black uppercase tracking-widest mb-1">Período de Análise</span>
        <span class="text-[11px] font-extralight tracking-luxury text-bracci-black uppercase">
          {{ formatDate(range.start) }} — {{ formatDate(range.end) }}
        </span>
      </div>
      <svg class="w-3 h-3 text-bracci-gold group-hover:translate-y-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Sophisticated Popover Overlay -->
    <Transition name="fade-slide">
      <div v-if="isOpen" class="absolute right-0 mt-4 z-50 bg-white border-thin border-gray-100 shadow-2xl flex p-6 min-w-[600px] backdrop-blur-xl">
        
        <!-- Sidebar Presets (Quick Access) -->
        <div class="w-40 border-r border-gray-50 flex flex-col gap-4 pr-6">
          <p class="text-[9px] text-bracci-gold font-black uppercase tracking-[0.3em] mb-4 italic">Presets VIP</p>
          <button @click="setPreset(7)" class="text-[10px] text-left text-gray-400 hover:text-bracci-black font-bold uppercase tracking-luxury transition-colors">Últimos 7 Dias</button>
          <button @click="setPreset(30)" class="text-[10px] text-left text-bracci-black font-bold uppercase tracking-luxury border-l-2 border-bracci-gold pl-3">Últimos 30 Dias</button>
          <button @click="setPreset(90)" class="text-[10px] text-left text-gray-400 hover:text-bracci-black font-bold uppercase tracking-luxury transition-colors">Trimestral</button>
          <button @click="setPreset(365)" class="text-[10px] text-left text-gray-400 hover:text-bracci-black font-bold uppercase tracking-luxury transition-colors">Anual (YTD)</button>
        </div>

        <!-- TAREFA: Implementação simplificada do v-calendar v3 -->
        <div class="flex-1 pl-6">
          <DatePicker 
            v-model.range="range" 
            mode="date"
            color="yellow" 
            :columns="2"
            class="luxury-calendar"
          />
          <div class="mt-6 pt-6 border-t border-gray-50 flex justify-end">
            <button @click="isOpen = false" class="bg-bracci-black text-white px-8 py-2 text-[10px] font-bold uppercase tracking-luxury hover:bg-bracci-gold transition-colors shadow-lg">
              Aplicar Intervalo
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style>
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-slide-enter-from, .fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Customizing V-Calendar to Bracci Standards */
.luxury-calendar {
  --vc-accent-600: #C5A059; /* Bracci Gold */
  border: none !important;
  background: transparent !important;
}
.vc-header { margin-bottom: 20px; }
.vc-title { font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.2em; font-weight: 800; font-family: 'Inter', sans-serif; }
.vc-weekday { font-size: 9px !important; text-transform: uppercase; font-weight: 400; color: #D1D5DB !important; }
.vc-day-content { font-size: 11px !important; font-weight: 300 !important; }
</style>
