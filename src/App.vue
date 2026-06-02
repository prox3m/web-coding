<template>
  <div class="container py-4 py-md-5">
    <!-- Заголовок -->
    <header class="text-center mb-4">
      <h1 class="display-5 fw-bold" style="background: var(--primary-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        😄 Random Jokes
      </h1>
      <p class="text-muted">Случайные шутки с озвучиванием на русском</p>
    </header>

    <!-- Карточка шутки -->
    <JokeCard 
      :joke="joke" 
      :loading="loading" 
      :error="error"
      @refresh="fetchJoke"
    />

    <!-- Раздел "О сервисе" -->
    <AboutSection />

    <!-- Футер -->
    <footer class="text-center text-muted small py-4">
      <p class="mb-0">Учебный проект • {{ new Date().getFullYear() }}</p>
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useJokeApi } from './composables/useJokeApi'
import JokeCard from './components/JokeCard.vue'
import AboutSection from './components/AboutSection.vue'

const { joke, loading, error, fetchJoke } = useJokeApi()

// Загружаем первую шутку при старте
onMounted(() => {
  fetchJoke()
})
</script>