<script setup>
import { ref } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  campaignName: String,
  copyData: Object,
  loading: Boolean
});

const emit = defineEmits(['close', 'generate']);
const copyFeedback = ref('');

const copyToClipboard = (text, field) => {
  navigator.clipboard.writeText(text);
  copyFeedback.value = field;
  setTimeout(() => copyFeedback.value = '', 2000);
};
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-12 bg-bracci-black/50 backdrop-blur-xl">
    <div class="bg-white w-full max-w-4xl shadow-2xl flex flex-col h-[80vh] border-thin border-white/20">
      <!-- Aesthetic Header -->
      <div class="p-12 border-b border-gray-50 flex justify-between items-center">
        <div>
          <h2 class="text-3xl font-light text-bracci-black tracking-tight-luxury uppercase">Elite <span class="font-extrabold">Copywriter</span></h2>
          <p class="text-[9px] text-bracci-gold tracking-luxury uppercase mt-1 font-bold italic">Bracci Intelligence Studio</p>
        </div>
        <button @click="emit('close')" class="text-bracci-black/20 hover:text-bracci-black transition-all text-4xl font-thin">&times;</button>
      </div>

      <!-- Designer Workspace -->
      <div class="flex-1 overflow-y-auto p-16 bg-bracci-offwhite/30">
        <div v-if="loading" class="flex flex-col items-center justify-center h-full gap-8">
          <div class="w-16 h-16 border-thin border-bracci-gold border-t-bracci-black animate-spin rounded-full"></div>
          <p class="text-[10px] tracking-[0.3em] uppercase text-gray-400 font-bold italic">Curating exclusive narratives...</p>
        </div>

        <div v-else-if="copyData" class="space-y-16 max-w-2xl mx-auto">
          <section class="space-y-4">
            <div class="flex justify-between items-center">
              <label class="text-[9px] font-black uppercase text-bracci-gold tracking-widest">Aesthetic Headline</label>
              <button @click="copyToClipboard(copyData.headline, 'headline')" class="text-[9px] uppercase font-bold text-gray-300 hover:text-bracci-gold transition-colors">
                {{ copyFeedback === 'headline' ? 'Copiado' : 'Copy' }}
              </button>
            </div>
            <p class="text-3xl font-extralight text-bracci-black tracking-tight leading-tight border-l-4 border-bracci-gold pl-10 py-2 italic">
              {{ copyData.headline }}
            </p>
          </section>

          <section class="space-y-4">
            <div class="flex justify-between items-center">
              <label class="text-[9px] font-black uppercase text-bracci-gold tracking-widest">Primary Narrative</label>
              <button @click="copyToClipboard(copyData.primary_text, 'body')" class="text-[9px] uppercase font-bold text-gray-300 hover:text-bracci-gold transition-colors">
                {{ copyFeedback === 'body' ? 'Copiado' : 'Copy' }}
              </button>
            </div>
            <div class="bg-white p-10 border-thin border-gray-100 shadow-sm text-sm leading-loose text-bracci-black/70 font-light italic">
              {{ copyData.primary_text }}
            </div>
          </section>

          <section class="space-y-4">
            <label class="text-[9px] font-black uppercase text-bracci-gold tracking-widest">Call to Action</label>
            <p class="text-xs text-bracci-black font-extrabold tracking-luxury underline uppercase italic">
              {{ copyData.description }}
            </p>
          </section>
        </div>

        <div v-else class="flex flex-col items-center justify-center h-full text-center gap-10">
          <p class="text-gray-300 font-light italic text-sm tracking-widest">Refine your brand presence with AI-driven luxury narratives.</p>
          <button @click="emit('generate')" class="bg-bracci-gold text-white px-16 py-5 text-[10px] font-extrabold uppercase tracking-luxury hover:bg-bracci-black transition-all shadow-xl">Start Narrative Generation</button>
        </div>
      </div>

      <!-- Bracci Standard Footer -->
      <div class="p-10 bg-white border-t border-gray-50 flex justify-between items-center">
        <p class="text-[8px] text-gray-300 tracking-[0.2em] uppercase font-bold italic">Standard: Luxo Tecnológico & 5-Year Guarantee</p>
        <button @click="emit('close')" class="px-12 py-4 text-[9px] font-extrabold uppercase tracking-luxury text-bracci-black border-thin border-bracci-black hover:bg-bracci-black hover:text-white transition-all">Close Studio</button>
      </div>
    </div>
  </div>
</template>
