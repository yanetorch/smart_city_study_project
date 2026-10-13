<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'
import { auth } from '../store'

const loading = ref(true)
const error = ref('')

// скрываем на всякий случай
const HIDDEN = ['hashed_password', 'password']
const safeUser = computed(() => {
  if (!auth.user) return null
  return Object.fromEntries(
    Object.entries(auth.user).filter(([k]) => !HIDDEN.includes(k))
  )
})

onMounted(async () => {
  try {
    const { data } = await api.get('/auth/users/me')
    auth.user = data
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="card">
    <h2>Профиль</h2>
    <p v-if="loading">Загрузка…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <table v-else-if="safeUser">
      <tbody>
        <tr v-for="(v, k) in safeUser" :key="k">
          <th style="width: 200px;">{{ k }}</th>
          <td>{{ v }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>