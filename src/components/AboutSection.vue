<template>
  <div class="about-section">
    <button 
      class="btn btn-outline-secondary w-100 d-flex justify-content-between align-items-center"
      @click="isExpanded = !isExpanded"
      :aria-expanded="isExpanded"
    >
      <span>ℹ️ Описание работы сервиса</span>
      <span>{{ isExpanded ? '▲ Скрыть' : '▼ Показать' }}</span>
    </button>
    
    <div v-show="isExpanded" class="mt-3">
      <h5>Назначение</h5>
      <p>Сервис показывает случайные шутки на английском языке с возможностью <strong>озвучивания на русском</strong> через встроенный синтезатор речи браузера.</p>
      
      <h5>API</h5>
      <ul class="small text-muted mb-3">
        <li>Источник: <a href="https://official-joke-api.appspot.com" target="_blank">Official Joke API</a> [[9]]</li>
        <li>Эндпоинт: <code>GET /random_joke</code></li>
        <li>Формат ответа: <code>{ setup, punchline, type }</code></li>
      </ul>
      
      <h5>Разработчик</h5>
      <p class="mb-0">
        <strong>Дмитрий Доронин</strong><br>
        doronindima997@gmail.com<br>
        GitHub: @prox3m<br>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const isExpanded = ref(false)
</script>