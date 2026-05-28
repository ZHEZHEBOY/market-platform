<template>
  <div class="analytics">
    <h2>数据报表</h2>

    <!-- 总览卡片 -->
    <div class="overview-cards">
      <div class="card" v-for="item in overviewItems" :key="item.label">
        <div class="card-value">{{ item.value }}</div>
        <div class="card-label">{{ item.label }}</div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="chart-card">
        <h3>销售趋势（近30天）</h3>
        <div ref="salesChart" class="chart"></div>
      </div>
      <div class="chart-card">
        <h3>用户增长（近30天）</h3>
        <div ref="userChart" class="chart"></div>
      </div>
      <div class="chart-card">
        <h3>订单状态分布</h3>
        <div ref="orderChart" class="chart"></div>
      </div>
      <div class="chart-card">
        <h3>分类销售排行</h3>
        <div ref="categoryChart" class="chart"></div>
      </div>
      <div class="chart-card full-width">
        <h3>热销商品 Top10</h3>
        <div ref="productChart" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import { getOverview, getSalesTrend, getUserGrowth, getOrderStatus, getCategorySales, getTopProducts } from '@/api/analytics'

const overview = ref({})
const salesChart = ref(null)
const userChart = ref(null)
const orderChart = ref(null)
const categoryChart = ref(null)
const productChart = ref(null)

let charts = []

const overviewItems = computed(() => [
  { label: '总用户数', value: overview.value.total_users || 0 },
  { label: '总订单数', value: overview.value.total_orders || 0 },
  { label: '总销售额', value: '¥' + ((overview.value.total_revenue || 0) / 100).toFixed(0) },
  { label: '总商品数', value: overview.value.total_products || 0 },
  { label: '总店铺数', value: overview.value.total_shops || 0 },
])

const initChart = (el, option) => {
  const chart = echarts.init(el)
  chart.setOption(option)
  charts.push(chart)
  return chart
}

const fetchAndRender = async () => {
  try {
    // 总览数据
    const overviewRes = await getOverview()
    overview.value = overviewRes.data

    // 销售趋势
    const salesRes = await getSalesTrend()
    initChart(salesChart.value, {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: salesRes.data.dates },
      yAxis: [
        { type: 'value', name: '销售额(元)' },
        { type: 'value', name: '订单数' }
      ],
      series: [
        {
          name: '销售额',
          type: 'line',
          data: salesRes.data.amounts.map(v => v / 100),
          smooth: true,
          itemStyle: { color: '#409eff' }
        },
        {
          name: '订单数',
          type: 'bar',
          yAxisIndex: 1,
          data: salesRes.data.counts,
          itemStyle: { color: '#67c23a' }
        }
      ]
    })

    // 用户增长
    const userRes = await getUserGrowth()
    initChart(userChart.value, {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: userRes.data.dates },
      yAxis: { type: 'value' },
      series: [{
        name: '新增用户',
        type: 'line',
        data: userRes.data.counts,
        smooth: true,
        areaStyle: { opacity: 0.3 },
        itemStyle: { color: '#e6a23c' }
      }]
    })

    // 订单状态分布
    const orderRes = await getOrderStatus()
    const statusMap = {
      pending_payment: '待付款',
      paid: '已付款',
      shipped: '已发货',
      signed: '已签收',
      cancelled: '已取消'
    }
    initChart(orderChart.value, {
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: orderRes.data.statuses.map((s, i) => ({
          name: statusMap[s] || s,
          value: orderRes.data.counts[i]
        })),
        label: { show: true, formatter: '{b}: {c}' }
      }]
    })

    // 分类销售排行
    const categoryRes = await getCategorySales()
    initChart(categoryChart.value, {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: categoryRes.data.categories, axisLabel: { rotate: 30 } },
      yAxis: { type: 'value', name: '销售额(元)' },
      series: [{
        name: '销售额',
        type: 'bar',
        data: categoryRes.data.amounts.map(v => v / 100),
        itemStyle: { color: '#409eff' }
      }]
    })

    // 热销商品 Top10
    const productRes = await getTopProducts()
    initChart(productChart.value, {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'value', name: '销量' },
      yAxis: {
        type: 'category',
        data: productRes.data.products,
        inverse: true,
        axisLabel: { width: 120, overflow: 'truncate' }
      },
      series: [{
        name: '销量',
        type: 'bar',
        data: productRes.data.quantities,
        itemStyle: { color: '#67c23a' }
      }]
    })
  } catch (e) {
    console.error('Failed to load analytics:', e)
  }
}

const handleResize = () => {
  charts.forEach(c => c.resize())
}

onMounted(() => {
  fetchAndRender()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach(c => c.dispose())
})
</script>

<style scoped>
.analytics {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.card-label {
  font-size: 14px;
  color: #666;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-card h3 {
  margin-bottom: 12px;
  font-size: 16px;
  color: #333;
}

.chart {
  height: 350px;
}
</style>
