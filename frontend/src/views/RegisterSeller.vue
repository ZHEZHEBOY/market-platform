<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const form = ref({ username: '', email: '', password: '', password2: '', shopName: '' })
const loading = ref(false)

async function handleRegister() {
  if (form.value.password !== form.value.password2) {
    ElMessage.error('两次密码不一致')
    return
  }
  if (!form.value.shopName.trim()) {
    ElMessage.error('请输入店铺名称')
    return
  }
  loading.value = true
  try {
    await userStore.registerSeller(form.value.username, form.value.email, form.value.password, form.value.shopName)
    ElMessage.success('注册成功，请等待店铺审核')
    router.push('/seller')
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
      <h2>卖家入驻</h2>
      <p class="subtitle">开设您的店铺，开始销售之旅</p>
      <el-form :model="form" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.email" placeholder="邮箱" prefix-icon="Message" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.shopName" placeholder="店铺名称" prefix-icon="Shop" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" show-password prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password2" type="password" placeholder="确认密码" show-password prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" block>申请入驻</el-button>
        </el-form-item>
      </el-form>
      <p class="tip">已有账号？<router-link to="/login">去登录</router-link></p>
      <p class="tip">想买东西？<router-link to="/register">买家注册</router-link></p>
    </el-card>
  </div>
</template>

<style scoped>
.form-page { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
.form-card { width: 440px; }
h2 { text-align: center; margin-bottom: 4px; }
.subtitle { text-align: center; color: var(--color-text-secondary); margin-bottom: 24px; font-size: 14px; }
.tip { text-align: center; color: #999; margin: 8px 0 0; font-size: 13px; }
</style>
