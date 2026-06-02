export const isSpeechSupported = () => {
  return 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window
}

export const translateText = async (text, from = 'en', to = 'ru') => {
  if (!text || typeof text !== 'string') return text
  
  try {
    // Очищаем текст от лишних переносов для корректного перевода
    const cleanText = text.trim().replace(/\s+/g, ' ')
    
    // Кодируем для URL
    const encodedText = encodeURIComponent(cleanText)
    const url = `https://api.mymemory.translated.net/get?q=${encodedText}&langpair=${from}|${to}`
    
    // Добавляем таймаут через AbortController
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 8000)
    
    const response = await fetch(url, { 
      signal: controller.signal,
      headers: { 'Accept': 'application/json' }
    })
    
    clearTimeout(timeoutId)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    
    if (data.responseStatus !== 200) {
      throw new Error(data.responseDetails || 'Ошибка перевода')
    }
    
    // Возвращаем переведённый текст или оригинал при ошибке
    return data.responseData?.translatedText?.trim() || text
  } catch (error) {
    if (error.name === 'AbortError') {
      console.warn('Translation timeout, using original')
    } else {
      console.warn('Translation failed:', error.message)
    }
    return text // Fallback к оригиналу
  }
}

export const speakText = async (text, options = {}) => {
  const {
    translate = false,   // Если false — текст уже переведён
    sourceLang = 'en',
    targetLang = 'ru',
    onEnd = null
  } = options

  if (!isSpeechSupported()) {
    console.warn('Web Speech API не поддерживается')
    return false
  }

  try {
    // Текст уже должен быть на нужном языке, если translate: false
    const textToSpeak = text?.trim()
    if (!textToSpeak) return false

    // Останавливаем предыдущее воспроизведение
    window.speechSynthesis.cancel()

    // Ждём инициализации голосов (критично для некоторых браузеров)
    await new Promise(resolve => {
      const voices = window.speechSynthesis.getVoices()
      if (voices.length > 0) {
        resolve()
      } else {
        const onVoicesChanged = () => {
          window.speechSynthesis.removeEventListener('voiceschanged', onVoicesChanged)
          resolve()
        }
        window.speechSynthesis.addEventListener('voiceschanged', onVoicesChanged)
        setTimeout(resolve, 300) // fallback
      }
    })

    const utterance = new SpeechSynthesisUtterance(textToSpeak)
    utterance.lang = targetLang === 'ru' ? 'ru-RU' : 'en-US'
    utterance.rate = 0.95
    utterance.pitch = 1.0
    utterance.volume = 1.0

    // Выбираем русский голос если доступен
    const voices = window.speechSynthesis.getVoices()
    const ruVoice = voices.find(v => 
      v.lang.toLowerCase().includes('ru') || 
      v.name.toLowerCase().includes('russian')
    )
    if (ruVoice) utterance.voice = ruVoice

    if (onEnd) {
      utterance.onend = onEnd
      utterance.onerror = (e) => {
        console.error('Speech error:', e)
        onEnd()
      }
    }

    window.speechSynthesis.speak(utterance)
    return true
  } catch (error) {
    console.error('Speech synthesis error:', error)
    return false
  }
}

export const stopSpeech = () => {
  if (isSpeechSupported()) {
    window.speechSynthesis.cancel()
  }
}

export const loadVoices = () => {
  return new Promise((resolve) => {
    if (!isSpeechSupported()) {
      resolve([])
      return
    }
    
    const voices = window.speechSynthesis.getVoices()
    if (voices.length > 0) {
      resolve(voices)
    } else {
      window.speechSynthesis.onvoiceschanged = () => {
        resolve(window.speechSynthesis.getVoices())
      }
      setTimeout(() => resolve(window.speechSynthesis.getVoices()), 500)
    }
  })
}