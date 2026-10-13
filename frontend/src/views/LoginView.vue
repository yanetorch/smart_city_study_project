<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { auth } from '../store'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await api.post('/auth/login', {
      username: username.value,
      password: password.value,
    })
    const token = data.access_token || data.token
    if (!token) throw new Error('Ошибка 401')
    auth.setToken(token)
    router.push('/profile')
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card" style="max-width: 400px; margin: 2rem auto;">
    <h2>Вход</h2>
    <form @submit.prevent="submit">
      <div class="field">
        <label>Логин</label>
        <input v-model="username" required autocomplete="username" />
      </div>
      <div class="field">
        <label>Пароль</label>
        <input v-model="password" type="password" required autocomplete="current-password" />
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="primary" :disabled="loading">
        {{ loading ? 'Входим…' : 'Войти' }}
      </button>
    </form>
    <p style="margin-top: 1rem;">
        <router-link to="/register">Зарегистрироваться</router-link>
    </p>
  </div>
</template>