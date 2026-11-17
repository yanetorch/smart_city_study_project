<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'

const sensors = ref([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/sensors')
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

            <p v-if="loading">Загрузка…</p>
            <p v-else-if="error" class="error">{{ error }}</p>

            <table v-else>
                <thead>
                    <tr>
                        <th>ID</th><th>Название</th><th>Расположение</th><th>Тип датчика</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="s in sensors":key="s.id">
                        <td>{{ s.id }}</td>
                        <td>{{ s.name }}</td>
                        <td>{{ s.location }}</td>
                        <td>{{ s.sensor_type}}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>