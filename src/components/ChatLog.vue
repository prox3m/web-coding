<template>
  <div class="card shadow-sm">
    <div class="card-header d-flex justify-content-between align-items-center bg-dark text-white">
      <span>🤖 Лог действий системы</span>
      <button class="btn btn-sm btn-outline-light" @click="clearLogs">🗑 Очистить логи</button>
    </div>
    <div class="card-body p-0">
      <div ref="chatContainer" class="chat-container p-3">
        <div v-for="log in logs" :key="log.id" class="chat-message system mb-2">
          <div class="message-content">
            <span class="time-badge">{{ log.time }}</span>
            <p class="mb-0">{{ log.text }}</p>
          </div>
        </div>
        <div v-if="logs.length === 0" class="text-center text-muted p-3">
          Действий пока не было...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { useFinanceManager } from '../composables/useFinanceManager.js';

const { logs, clearLogs } = useFinanceManager();
const chatContainer = ref(null);

// Автопрокрутка вниз при появлении нового сообщения
watch(logs, async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
}, { deep: true });
</script>

<style scoped>
.chat-container {
  height: 350px;
  overflow-y: auto;
  background-color: #f8f9fa;
}
.chat-message.system {
  display: flex;
  justify-content: flex-start;
}
.message-content {
  background-color: #e9ecef;
  color: #212529;
  padding: 8px 12px;
  border-radius: 12px 12px 12px 2px;
  max-width: 90%;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.time-badge {
  font-size: 0.7rem;
  color: #6c757d;
  display: block;
  margin-bottom: 2px;
}
</style>