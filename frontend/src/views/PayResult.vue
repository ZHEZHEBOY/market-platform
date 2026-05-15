<script setup>
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()
</script>
<template>
  <div style="padding:40px;text-align:center">
    <h2>支付结果</h2>
    <p>订单号: {{ route.query.out_trade_no }}</p>
    <p>请到「我的订单」查看最新状态</p>
    <el-button type="primary" @click="router.push('/orders')">查看订单</el-button>
  </div>
</template>
