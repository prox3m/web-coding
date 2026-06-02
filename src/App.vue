<template>
  <div class="container py-4">
    <h1 class="text-center mb-4 text-primary fw-bold">💰 Инвестиционный Трекер</h1>
    <div class="row g-4">
      <div class="col-lg-7">
        <FinanceForm />
        <RecentOperations />
      </div>
      <div class="col-lg-5">
        <ChatLog />
      </div>
    </div>
  </div>
</template>

<script setup>
import FinanceForm from './components/FinanceForm.vue';
import ChatLog from './components/ChatLog.vue';
import RecentOperations from './components/RecentOperations.vue';
</script>