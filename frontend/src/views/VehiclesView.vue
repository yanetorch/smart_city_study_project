<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'

const vehicles = ref([])
const loading = ref(true)
const error = ref('')

const filterType = ref('')
const filterStatus = ref('')

const filtered = computed(() =>
  vehicles.value.filter((v) =>
    (!filterType.value || v.vehicle_type === filterType.value) &&
    (!filterStatus.value || v.status === filterStatus.value)
  )
)

const typeLabels = { bus: 'Автобус', tram: 'Трамвай', trolleybus: 'Троллейбус' }
const statusLabels = { active: 'В пути', in_depot: 'В депо', maintenance: 'Обслуживание' }

function fmtTime(s) {
  return s ? new Date(s).toLocaleString('ru-RU') : '—'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/transport/vehicles')
    vehicles.value = data
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
      <h2>Транспорт</h2>
      <button @click="load">Обновить</button>
    </div>

    <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
      <label style="flex: 1;">
        Тип:
        <select v-model="filterType">
          <option value="">Все</option>
          <option value="bus">Автобус</option>
          <option value="tram">Трамвай</option>
          <option value="trolleybus">Троллейбус</option>
        </select>
      </label>
      <label style="flex: 1;">
        Статус:
        <select v-model="filterStatus">
          <option value="">Все</option>
          <option value="active">В пути</option>
          <option value="in_depot">В депо</option>
          <option value="maintenance">Обслуживание</option>
        </select>
      </label>
    </div>

    <p v-if="loading">Загрузка…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th><th>Тип</th><th>Маршрут</th><th>Госномер</th>
          <th>Координаты</th><th>Статус</th><th>Обновлено</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="v in filtered" :key="v.id">
          <td>{{ v.id }}</td>
          <td>{{ typeLabels[v.vehicle_type] || v.vehicle_type }}</td>
          <td>{{ v.route_number }}</td>
          <td>{{ v.plate_number }}</td>
          <td>{{ v.latitude.toFixed(5) }}, {{ v.longitude.toFixed(5) }}</td>
          <td>{{ statusLabels[v.status] || v.status }}</td>
          <td>{{ fmtTime(v.updated_at) }}</td>
        </tr>
      </tbody>
    </table>
    <p v-if="!loading && !filtered.length">Ничего не найдено</p>
  </div>
</template>