<script setup lang="ts">
import { ref, onMounted } from 'vue'

const appVersion = ref('')
const modelVersion = ref('')

onMounted(async () => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL; // e.g., http://localhost:3000
    const endpointAppVersion = `${apiUrl}/version/app`;

    const appRes = await fetch(endpointAppVersion)
    const appData = await appRes.json()
    appVersion.value = appData.version

    const endpointModelVersion = `${apiUrl}/version/model`;
    const modelRes = await fetch(endpointModelVersion)
    const modelData = await modelRes.json()
    modelVersion.value = modelData.modelVersion
  } catch (err) {
    console.error('Failed to fetch version info:', err)
  }
})
</script>

<template>
  <div class="version-box">
    <div><strong>App version:</strong> {{ appVersion }}</div>
    <div><strong>Model version:</strong> {{ modelVersion }}</div>
  </div>
</template>

<style scoped>
.version-box {
  position: fixed;
  bottom: 2vh;
  right: 1vw;
  background-color: #f9f9f9;
  border: 1px solid #ccc;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  font-size: 14px;
  z-index: 1000;
}
</style>
