<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'

const sensors = ref([])
const loading = ref(true)
const error = ref('')

const filterType = ref('')

const filtered = computed(() =>
  sensors.value.filter((s) =>
    !filterType.value || s.sensor_type === filterType.value
  )
)

const typeLabels = {
  temperature: 'Температура',
  air_quality: 'Качество воздуха',
  noise: 'Уровень шума',
  humidity: 'Влажность',
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/environment/sensors')
    sensors.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h2>Датчики</h2>
      <button @click="load">Обновить</button>
    </div>

    <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
      <label style="flex: 1;">
        Тип:
        <select v-model="filterType">
          <option value="">Все</option>
          <option value="temperature">Температура</option>
          <option value="air_quality">Качество воздуха</option>
          <option value="noise">Уровень шума</option>
          <option value="humidity">Влажность</option>
        </select>
      </label>
    </div>

    <p v-if="loading">Загрузка…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th><th>Название</th><th>Расположение</th><th>Тип датчика</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="s in filtered" :key="s.id">
          <td>{{ s.id }}</td>
          <td>{{ s.name }}</td>
          <td>{{ s.location }}</td>
          <td>{{ typeLabels[s.sensor_type] || s.sensor_type }}</td>
        </tr>
      </tbody>
    </table>
    <p v-if="!loading && !filtered.length">Ничего не найдено</p>
  </div>
</template>