<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'

const issues = ref([])
const loading = ref(true)
const error = ref('')

const filterStatus = ref('')

const statusLabels = {
  new: 'Новая',
  in_progress: 'В работе',
  resolved: 'Решена',
  rejected: 'Отклонена',
}
const categoryLabels = {
  water: 'Вода',
  heating: 'Отопление',
  electricity: 'Электричество',
  garbage: 'Мусор',
  road: 'Дорога',
  other: 'Другое',
}

const filtered = computed(() =>
  issues.value.filter((i) => !filterStatus.value || i.status === filterStatus.value)
)

const creating = ref(false)
const form = ref({ title: '', description: '', address: '', category: 'water' })
const formError = ref('')
const submitting = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/utility/issues')
    issues.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  } finally {
    loading.value = false
  }
}

async function submitCreate() {
  formError.value = ''
  submitting.value = true
  try {
    await api.post('/utility/issues', form.value)
    creating.value = false
    form.value = { title: '', description: '', address: '', category: 'water' }
    await load()
  } catch (e) {
    formError.value = e.response?.data?.detail || e.message
  } finally {
    submitting.value = false
  }
}

async function changeStatus(issue, newStatus) {
  const comment = prompt(`Комментарий к смене статуса «${statusLabels[newStatus]}» (необязательно):`)
  if (comment === null) return
  try {
    await api.put(`/utility/issues/${issue.id}`, { status: newStatus, comment: comment || null })
    await load()
  } catch (e) {
    alert(e.response?.data?.detail || e.message)
  }
}

function fmtTime(s) {
  return s ? new Date(s).toLocaleString('ru-RU') : '—'
}

onMounted(load)
</script>

<template>
  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h2>Заявки ЖКХ</h2>
      <div style="display: flex; gap: 0.5rem;">
        <button @click="load">Обновить</button>
        <button class="primary" @click="creating = !creating">
          {{ creating ? 'Отмена' : 'Новая заявка' }}
        </button>
      </div>
    </div>

    <div v-if="creating" class="card" style="background: #f0f0f2;">
      <h3>Новая заявка</h3>
      <form @submit.prevent="submitCreate">
        <div class="field">
          <label>Заголовок</label>
          <input v-model="form.title" required maxlength="200" />
        </div>
        <div class="field">
          <label>Описание</label>
          <textarea v-model="form.description" required rows="3"></textarea>
        </div>
        <div class="field">
          <label>Адрес</label>
          <input v-model="form.address" required maxlength="255" />
        </div>
        <div class="field">
          <label>Категория</label>
          <select v-model="form.category" required>
            <option v-for="(label, val) in categoryLabels" :key="val" :value="val">
              {{ label }}
            </option>
          </select>
        </div>
        <p v-if="formError" class="error">{{ formError }}</p>
        <button class="primary" :disabled="submitting">
          {{ submitting ? 'Отправляем…' : 'Создать' }}
        </button>
      </form>
    </div>

    <div style="margin: 1rem 0;">
      <label>
        Статус:
        <select v-model="filterStatus" style="width: auto;">
          <option value="">Все</option>
          <option v-for="(label, val) in statusLabels" :key="val" :value="val">
            {{ label }}
          </option>
        </select>
      </label>
    </div>

    <p v-if="loading">Загрузка…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th><th>Заголовок</th><th>Адрес</th>
          <th>Категория</th><th>Статус</th><th>Создана</th><th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="i in filtered" :key="i.id">
          <td>{{ i.id }}</td>
          <td>{{ i.title }}</td>
          <td>{{ i.address }}</td>
          <td>{{ categoryLabels[i.category] || i.category }}</td>
          <td>{{ statusLabels[i.status] || i.status }}</td>
          <td>{{ fmtTime(i.created_at) }}</td>
          <td>
            <select
              :value="i.status"
              @change="changeStatus(i, $event.target.value)"
              style="width: auto;"
            >
              <option v-for="(label, val) in statusLabels" :key="val" :value="val">
                {{ label }}
              </option>
            </select>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="!loading && !filtered.length">Заявок нет</p>
  </div>
</template>