<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const form = ref({ username: '', password: '' })
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    await userStore.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="form-page">
    <el-card class="form-card">
      <h2>登录</h2>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" block>登录</el-button>
        </el-form-item>
      </el-form>
      <p class="tip">没有账号？<router-link to="/register">去注册</router-link></p>
    </el-card>
  </div>
</template>

<style scoped>
.form-page { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
.form-card { width: 400px; }
h2 { text-align: center; margin-bottom: 20px; }
.tip { text-align: center; color: #999; }
</style>
