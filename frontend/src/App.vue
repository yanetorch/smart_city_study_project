<script setup>
import { onMounted } from 'vue'
import NavBar from './NavBar.vue'
import { auth } from './store'

onMounted(() => {
  auth.loadUser()   // не await — фон
})
</script>

<template>
  <NavBar />
  <div class="container">
    <router-view />
  </div>
</template>