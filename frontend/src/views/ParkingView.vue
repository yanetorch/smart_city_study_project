<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const parkings = ref([])
const loading = ref(true)
const error = ref('')

const reserving = ref(null)
const form = ref({ car_number: '', start_time: '', end_time: '' })
const formError = ref('')
const submitting = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/transport/parking')
    parkings.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  } finally {
    loading.value = false
  }
}

function openReserve(p) {
  reserving.value = p
  formError.value = ''
  const now = new Date()
  const inHour = new Date(now.getTime() + 60 * 60 * 1000)
  form.value = {
    car_number: '',
    start_time: toLocalInput(now),
    end_time: toLocalInput(inHour),
  }
}

function toLocalInput(d) {
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function submitReserve() {
  formError.value = ''
  submitting.value = true
  try {
    await api.post(`/transport/parking/${reserving.value.id}/reserve`, {
      car_number: form.value.car_number,
      start_time: new Date(form.value.start_time).toISOString(),
      end_time: new Date(form.value.end_time).toISOString(),
    })
    reserving.value = null
  } catch (e) {
    formError.value = e.response?.data?.detail || e.message
  } finally {
    submitting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h2>Парковки</h2>
      <button @click="load">Обновить</button>
    </div>

    <p v-if="loading">Загрузка…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th><th>Название</th><th>Адрес</th>
          <th>Мест</th><th>Цена/час</th><th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in parkings" :key="p.id">
          <td>{{ p.id }}</td>
          <td>{{ p.name }}</td>
          <td>{{ p.address }}</td>
          <td>{{ p.total_spots }}</td>
          <td>{{ p.price_per_hour }} ₽</td>
          <td><button @click="openReserve(p)">Забронировать</button></td>
        </tr>
      </tbody>
    </table>
    <p v-if="!loading && !parkings.length">Парковок нет</p>
  </div>

  <div v-if="reserving" class="card" style="border: 2px solid #2c3e50;">
    <h3>Бронирование: {{ reserving.name }}</h3>
    <p>Адрес: {{ reserving.address }}</p>
    <form @submit.prevent="submitReserve">
      <div class="field">
        <label>Номер автомобиля</label>
        <input v-model="form.car_number" required placeholder="А123БВ777" />
      </div>
      <div class="field">
        <label>Начало</label>
        <input v-model="form.start_time" type="datetime-local" required />
      </div>
      <div class="field">
        <label>Окончание</label>
        <input v-model="form.end_time" type="datetime-local" required />
      </div>
      <p v-if="formError" class="error">{{ formError }}</p>
      <div style="display: flex; gap: 0.5rem;">
        <button class="primary" :disabled="submitting">
          {{ submitting ? 'Отправляем…' : 'Забронировать' }}
        </button>
        <button type="button" @click="reserving = null">Отмена</button>
      </div>
    </form>
  </div>
</template>