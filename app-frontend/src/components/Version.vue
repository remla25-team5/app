<script setup lang="ts">
import { ref, onMounted } from 'vue'

const appVersion = ref('')
const modelVersion = ref('')

// Use environment variables for API base URL
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';

onMounted(async () => {
  try {
    const endpointAppVersion = `${apiBaseUrl}/version/app`;

    const appRes = await fetch(endpointAppVersion);
    if (!appRes.ok) {  // If the status is not 200
      const errorMessage = `Failed to fetch app version. Status: ${appRes.status}`;
      alert(`${errorMessage} - ${await appRes.text()}`); // Show both status and response message
      throw new Error(errorMessage);
    }
    const appData = await appRes.json();
    appVersion.value = appData.version;

    const endpointModelVersion = `${apiBaseUrl}/version/model`;
    const modelRes = await fetch(endpointModelVersion);
    if (!modelRes.ok) {  // If the status is not 200
      const errorMessage = `Failed to fetch model version. Status: ${modelRes.status}`;
      alert(`${errorMessage} - ${await modelRes.text()}`); // Show both status and response message
      throw new Error(errorMessage);
    }
    const modelData = await modelRes.json();
    modelVersion.value = modelData.version || modelData.modelVersion;

  } catch (err) {
    console.error('Error fetching version info:', err);
    alert(`There was an issue fetching version info. Please try again later.`);
  }
});

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
