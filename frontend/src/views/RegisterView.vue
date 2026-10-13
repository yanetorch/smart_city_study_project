<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const form = ref({ username: '', email: '', password: '' })
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await api.post('/auth/register', form.value)
    router.push('/login')
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card" style="max-width: 400px; margin: 2rem auto;">
    <h2>Регистрация</h2>
    <form @submit.prevent="submit">
      <div class="field">
        <label>Логин</label>
        <input v-model="form.username" required />
      </div>
      <div class="field">
        <label>Почта</label>
        <input v-model="form.email" type="email" required />
      </div>
      <div class="field">
        <label>Пароль</label>
        <input v-model="form.password" type="password" required minlength="6" />
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="primary" :disabled="loading">
        {{ loading ? 'Создаём…' : 'Зарегистрироваться' }}
      </button>
    </form>
    <p style="margin-top: 1rem;">
        <router-link to="/login">Войти</router-link>
    </p>
  </div>
</template>