<script setup>
import { ref } from 'vue';
import api from '../services/api';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close', 'refresh']);
const isDragging = ref(false);
const uploading = ref(false);

const handleFileUpload = async (event) => {
  const file = event.target.files[0] || event.dataTransfer.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  try {
    uploading.value = true;
    await api.post('/campaigns/import-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    alert("Dados Bracci importados com sucesso.");
    emit('refresh');
    emit('close');
  } catch (error) {
    alert("Erro ao importar CSV. Verifique o formato.");
  } finally {
    uploading.value = false;
    isDragging.value = false;
  }
};
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-8 bg-bracci-black/40 backdrop-blur-sm">
    <div class="bg-white w-full max-w-xl shadow-2xl p-12">
      <div class="flex justify-between items-start mb-12">
        <div>
          <h2 class="text-2xl font-light tracking-luxury uppercase">Data <span class="font-extrabold">Ingestion</span></h2>
          <p class="text-[9px] text-bracci-gold uppercase tracking-widest mt-1">Meta Ads & Mlabs Import</p>
        </div>
        <button @click="emit('close')" class="text-3xl font-thin hover:text-bracci-gold transition-colors">&times;</button>
      </div>

      <div 
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleFileUpload"
        class="border-thin border-dashed h-64 flex flex-col items-center justify-center transition-all"
        :class="isDragging ? 'border-bracci-gold bg-bracci-offwhite' : 'border-gray-200 bg-white'"
      >
        <div v-if="uploading" class="animate-spin rounded-full h-8 w-8 border-b-2 border-bracci-gold"></div>
        <div v-else class="text-center cursor-pointer" @click="$refs.fileInput.click()">
          <p class="text-[11px] tracking-luxury uppercase font-bold text-bracci-black">Arraste seu CSV aqui</p>
          <p class="text-[9px] text-gray-400 mt-2 uppercase tracking-widest italic">ou clique para selecionar arquivo</p>
          <input type="file" ref="fileInput" class="hidden" @change="handleFileUpload" accept=".csv" />
        </div>
      </div>

      <div class="mt-12 flex justify-end">
        <button @click="emit('close')" class="text-[10px] uppercase tracking-luxury font-bold text-gray-400 hover:text-bracci-black transition-colors">Cancelar</button>
      </div>
    </div>
  </div>
</template>
