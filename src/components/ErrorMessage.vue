<template>
  <div v-if="message" class="alert alert-danger error-alert d-flex align-items-center" role="alert">
    <i class="bi bi-exclamation-triangle-fill me-2 fs-4"></i>
    <div>{{ message }}</div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: ''
  }
})
</script>