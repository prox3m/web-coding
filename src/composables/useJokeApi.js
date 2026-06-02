import { ref } from 'vue'
import axios from 'axios'

const API_URL = 'https://official-joke-api.appspot.com/random_joke'

export function useJokeApi() {
  const joke = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchJoke = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Добавляем таймаут для обработки недоступности API
      const response = await axios.get(API_URL, { timeout: 8000 })
      
      // Валидация ответа
      if (!response.data?.setup || !response.data?.punchline) {
        throw new Error('Пустой или некорректный ответ от API')
      }
      
      joke.value = {
        setup: response.data.setup,
        punchline: response.data.punchline,
        type: response.data.type || 'general'
      }
    } catch (err) {
      console.error('API Error:', err)
      error.value = err.message.includes('timeout') 
        ? 'Сервис временно недоступен. Проверьте подключение к интернету.'
        : 'Не удалось загрузить шутку. Попробуйте позже.'
      joke.value = null
    } finally {
      loading.value = false
    }
  }

  return { joke, loading, error, fetchJoke }
}