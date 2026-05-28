<script setup>
import Navbar from './components/Navbar.vue'
</script>

<template>
  <Navbar />
  <router-view />
</template>

<style>
:root {
  --color-primary: #FF6700;
  --color-primary-light: #FF8533;
  --color-primary-dark: #E55D00;
  --color-text: #333333;
  --color-text-secondary: #757575;
  --color-text-light: #B0B0B0;
  --color-bg: #F5F5F5;
  --color-bg-white: #FFFFFF;
  --color-border: #E0E0E0;
  --color-price: #FF6700;
  --shadow-card: 0 2px 12px rgba(0, 0, 0, 0.08);
  --shadow-card-hover: 0 8px 24px rgba(0, 0, 0, 0.12);
  --radius-card: 12px;
  --radius-button: 8px;
  --radius-input: 8px;
  --header-height: 60px;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, 'Helvetica Neue', Arial, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  color: var(--color-text);
  background-color: var(--color-bg);
  -webkit-font-smoothing: antialiased;
}

a {
  color: inherit;
  text-decoration: none;
}

img {
  display: block;
}
</style>
