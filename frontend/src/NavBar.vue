<script setup>
import { useRouter } from 'vue-router'
import { auth } from './store'

const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <nav>
    <router-link to="/vehicles">Транспорт</router-link>
    <router-link to="/parking">Парковки</router-link>
    <router-link to="/issues">ЖКХ</router-link>
    <span class="spacer"></span>
    <template v-if="auth.isAuthenticated">
      <router-link to="/profile">Профиль</router-link>
      <button @click="logout">Выйти</button>
    </template>
    <template v-else>
      <router-link to="/login">Вход</router-link>
      <router-link to="/register">Регистрация</router-link>
    </template>
  </nav>
</template>