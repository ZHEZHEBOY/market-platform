<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const form = ref({ username: '', email: '', password: '', password2: '' })
const loading = ref(false)

async function handleRegister() {
  if (form.value.password !== form.value.password2) {
    ElMessage.error('两次密码不一致')
    return
  }
  loading.value = true
  try {
    await userStore.register(form.value.username, form.value.email, form.value.password)
    ElMessage.success('注册成功')
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
      <h2>注册</h2>
      <el-form :model="form" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.email" placeholder="邮箱" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password2" type="password" placeholder="确认密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" block>注册</el-button>
        </el-form-item>
      </el-form>
      <p class="tip">已有账号？<router-link to="/login">去登录</router-link></p>
    </el-card>
  </div>
</template>

<style scoped>
.form-page { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
.form-card { width: 400px; }
h2 { text-align: center; margin-bottom: 20px; }
.tip { text-align: center; color: #999; }
</style>
