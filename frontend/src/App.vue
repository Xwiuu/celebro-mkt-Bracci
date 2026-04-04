<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const notification = ref(null);

const showNotification = (msg) => {
  notification.value = msg;
  setTimeout(() => notification.value = null, 3000);
};
</script>

<template>
  <div class="min-h-screen flex bg-bracci-offwhite font-sans text-bracci-black">
    
    <!-- Notification Toast -->
    <Transition name="fade">
      <div v-if="notification" class="fixed top-12 left-1/2 -translate-x-1/2 z-[100] bg-bracci-black text-bracci-gold border border-bracci-gold px-12 py-4 shadow-2xl font-bold uppercase tracking-widest text-[10px] italic">
        {{ notification }}
      </div>
    </Transition>

    <!-- Luxury Sidebar -->
    <aside class="w-72 bg-white border-r border-gray-100 flex flex-col p-12 fixed h-full z-10">
      <div class="mb-20">
        <h1 class="text-3xl font-extrabold tracking-luxury uppercase cursor-pointer" @click="router.push('/')">Bracci</h1>
        <p class="text-[9px] text-bracci-gold tracking-[0.4em] uppercase mt-2 font-light italic">Intelligence OS</p>
      </div>

      <nav class="flex flex-col gap-10">
        <router-link to="/dashboard" class="text-[11px] tracking-luxury uppercase transition-all" active-class="text-bracci-black font-extrabold border-b-2 border-bracci-gold w-max pb-1" inactive-class="text-gray-300 hover:text-bracci-black">
          Executive View
        </router-link>
        <router-link to="/comparativo" class="text-[11px] tracking-luxury uppercase transition-all" active-class="text-bracci-black font-extrabold border-b-2 border-bracci-gold w-max pb-1" inactive-class="text-gray-300 hover:text-bracci-black">
          Performance Delta
        </router-link>
        <router-link to="/celebro" class="text-[11px] tracking-luxury uppercase transition-all" active-class="text-bracci-black font-extrabold border-b-2 border-bracci-gold w-max pb-1" inactive-class="text-gray-300 hover:text-bracci-black">
          Neuro-Sócio IA
        </router-link>
      </nav>

      <!-- Secret Footer Link -->
      <div class="mt-auto">
        <p class="text-[8px] text-gray-200 tracking-[0.2em] uppercase text-center italic hover:text-gray-400 transition-colors cursor-default">
          Standard V3.0 Final System
        </p>
      </div>
    </aside>

    <!-- Content Area -->
    <main class="flex-1 ml-72 p-20">
      <router-view v-slot="{ Component }">
        <transition name="fade-page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.4s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.fade-page-enter-active, .fade-page-leave-active { transition: all 0.3s ease; }
.fade-page-enter-from { opacity: 0; transform: translateY(10px); }
.fade-page-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
