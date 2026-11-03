<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'

const invoices = ref([])
const loading = ref(true)
const error = ref('')

const creating = ref(false)
const form = ref({ title: '', description: '', address: '', category: 'water' })
const formError = ref('')
const submitting = ref(false)

// async function load() {
//   loading.value = true
//   error.value = ''
//   try {
//     const { data } = await api.get('')
//     issues.value = data
//   } catch (e) {
//     error.value = e.response?.data?.detail || e.message
//   } finally {
//     loading.value = false
//   }
// }

onMounted(load)
</script>

<template>
  <div class="card">
  </div>
</template>