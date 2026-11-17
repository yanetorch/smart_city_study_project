<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'
import { auth } from '../store'

const invoices = ref([])
const loading = ref(true)
const error = ref('')

const filterStatus = ref('')

const payingId = ref(null)
const payError = ref('')
const paySuccess = ref('')

const filtered = computed(() =>
  invoices.value.filter((inv) =>
    !filterStatus.value || inv.status === filterStatus.value
  )
)

const statusLabels = {
  pending: 'Ожидает оплаты',
  paid: 'Оплачен',
}

function fmtMoney(v) {
  return v != null ? v.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' ₽' : '—'
}

function fmtTime(s) {
  return s ? new Date(s).toLocaleString('ru-RU') : '—'
}

const currentUserId = computed(() => auth.user?.id ?? null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    if (!currentUserId.value) {
      await auth.loadUser()
      if (!currentUserId.value) throw new Error('Не удалось определить пользователя')
    }
    const { data } = await api.get(`/billing/accounts/${currentUserId.value}/invoices`)
    invoices.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  } finally {
    loading.value = false
  }
}

async function pay(invoice) {
  payingId.value = invoice.id
  payError.value = ''
  paySuccess.value = ''
  try {
    await api.post('/billing/payments', {
      invoice_id: invoice.id,
      amount: invoice.amount,
    })
    paySuccess.value = `Счёт #${invoice.id} оплачен`
    await load()
  } catch (e) {
    payError.value = e.response?.data?.detail || e.message
  } finally {
    payingId.value = null
  }
}

onMounted(load)
</script>

<template>
  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h2>Счета</h2>
      <button @click="load">Обновить</button>
    </div>

    <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
      <label style="flex: 1;">
        Статус:
        <select v-model="filterStatus">
          <option value="">Все</option>
          <option value="pending">Ожидает оплаты</option>
          <option value="paid">Оплачен</option>
        </select>
      </label>
    </div>

    <p v-if="paySuccess" class="success">{{ paySuccess }}</p>
    <p v-if="payError" class="error">{{ payError }}</p>

    <p v-if="loading">Загрузка…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th><th>Сумма</th><th>Статус</th><th>Создан</th><th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="inv in filtered" :key="inv.id">
          <td>{{ inv.id }}</td>
          <td>{{ fmtMoney(inv.amount) }}</td>
          <td>{{ statusLabels[inv.status] || inv.status }}</td>
          <td>{{ fmtTime(inv.created_at) }}</td>
          <td>
            <button
              v-if="inv.status === 'pending'"
              :disabled="payingId === inv.id"
              @click="pay(inv)"
            >
              {{ payingId === inv.id ? 'Оплата…' : 'Оплатить' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="!loading && !filtered.length">Счетов нет</p>
  </div>
</template>