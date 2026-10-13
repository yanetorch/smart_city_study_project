<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const user = ref(null)
const loading = ref(true)
const error = ref('')

const PUBLIC_FIELDS = ['username', 'email']

const publicUser = computed(() => {
  if (!user.value) return null
  return Object.fromEntries(
    Object.entries(user.value).filter(([k]) => PUBLIC_FIELDS.includes(k))
  )
})

const fieldLabels = {
  username: 'Имя пользователя',
  email: 'Email',
}

onMounted(async () => {
  try {
    const { data } = await api.get(`/auth/users/${route.params.id}`)
    user.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="card">
    <router-link to="/issues">← Назад</router-link>
    <h2>Пользователь #{{ route.params.id }}</h2>

    <p v-if="loading">Загрузка…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <table v-else-if="publicUser">
      <tbody>
        <tr v-for="(v, k) in publicUser" :key="k">
          <th style="width: 220px;">{{ fieldLabels[k] || k }}</th>
          <td>{{ v }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>