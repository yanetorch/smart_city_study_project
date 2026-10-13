import { reactive } from 'vue'

export const auth = reactive({
  token: localStorage.getItem('token') || null,
  user: null,

  setToken(token) {
    this.token = token
    if (token) localStorage.setItem('token', token)
    else localStorage.removeItem('token')
  },

  logout() {
    this.setToken(null)
    this.user = null
  },

  get isAuthenticated() {
    return !!this.token
  },
})