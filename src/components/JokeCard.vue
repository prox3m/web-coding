<template>
  <div class="card joke-card p-4">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p class="mt-3 text-muted">Загружаем шутку...</p>
    </div>
    
    <ErrorMessage v-else-if="error" :message="error" />
    
    <template v-else-if="joke">
      <span class="badge bg-secondary mb-3">{{ joke.type }}</span>
      
      <!-- Setup (вопрос/подготовка шутки) -->
      <p class="setup-text">{{ joke.setup }}</p>
      
      <!-- Punchline (панчлайн) с опцией показа перевода -->
      <div class="punchline-wrapper">
        <p class="punchline-text">🎯 {{ joke.punchline }}</p>
        
        <!-- Перевод панчлайна (показывается после перевода) -->
        <p v-if="translatedPunchline" class="punchline-text mt-2 text-primary border-top pt-2">
          🇷🇺 {{ translatedPunchline }}
        </p>
      </div>
      
      <div class="d-flex gap-2 mt-4 flex-wrap">
        <button 
          class="btn btn-speak"
          @click="handleSpeak"
          :disabled="!speechSupported || isSpeaking || isTranslating"
        >
          <span v-if="isTranslating">🔄 Перевод...</span>
          <span v-else-if="isSpeaking">🔊 Озвучивается...</span>
          <span v-else>🔈 Озвучить на русском</span>
        </button>
        
        <button 
          class="btn btn-outline-primary"
          @click="$emit('refresh')"
          :disabled="loading || isSpeaking"
        >
          🔄 Новая шутка
        </button>
      </div>
      
      <small class="text-muted mt-3 d-block">
        💡 Перевод через MyMemory API • Озвучивание: Chrome/Edge/Safari
      </small>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { isSpeechSupported, speakText, stopSpeech, loadVoices } from '../utils/speech'
import ErrorMessage from './ErrorMessage.vue'

const props = defineProps({
  joke: Object,
  loading: Boolean,
  error: String
})

defineEmits(['refresh'])

const isSpeaking = ref(false)
const isTranslating = ref(false)
const translatedPunchline = ref('')
const speechSupported = isSpeechSupported()

// Предзагружаем голоса при монтировании
onMounted(async () => {
  await loadVoices()
  window.addEventListener('beforeunload', stopSpeech)
})

onBeforeUnmount(() => {
  stopSpeech()
  window.removeEventListener('beforeunload', stopSpeech)
})

const handleSpeak = async () => {
  if (!props.joke || isSpeaking.value) return
  
  // Объединяем setup и punchline
  const fullText = `${props.joke.setup}. ${props.joke.punchline}`
  
  isTranslating.value = true
  
  try {
    // 1. Сначала переводим панчлайн для отображения (опционально)
    if (!translatedPunchline.value) {
      const { translateText } = await import('../utils/speech')
      translatedPunchline.value = await translateText(props.joke.punchline)
    }
    
    // 2. Озвучиваем полный текст с переводом
    isTranslating.value = false
    isSpeaking.value = true
    
    const success = await speakText(fullText, {
      translate: true,
      sourceLang: 'en',
      targetLang: 'ru',
      onEnd: () => {
        isSpeaking.value = false
      }
    })
    
    if (!success) {
      alert('Не удалось озвучить. Попробуйте другой браузер (Chrome/Edge).')
      isSpeaking.value = false
    }
  } catch (error) {
    console.error('Speak error:', error)
    isTranslating.value = false
    isSpeaking.value = false
    alert('Ошибка при озвучивании. Проверьте подключение к интернету.')
  }
}
</script>

<style scoped>
.punchline-wrapper {
  transition: all 0.3s ease;
}

.punchline-text {
  margin-bottom: 0;
  line-height: 1.5;
}
</style>