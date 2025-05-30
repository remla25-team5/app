<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  submissionId: {
    type: String,
    required: true
  }
})

// Use environment variables for API base URL
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
// const apiBaseUrl = 'http://localhost:8080/api';
const statusMessage = ref('')
const verificationProcessed = ref(false)

watch(
    () => props.submissionId,
    () => {
      verificationProcessed.value = false
      statusMessage.value = ''
    }
)

// Function to send verification request to the backend
const verifySentiment = async (isCorrect) => {
  const endpoint = `${apiBaseUrl}/verify`

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        submissionId: props.submissionId,
        isCorrect: isCorrect,
      }),
    })

    if (response.ok) {
      const result = await response.json()
      console.log('Verification result:', result)
      console.log('Verified:', result.verified)
      verificationProcessed.value = true
      statusMessage.value = result.verified ? 'Thanks, your verification has been processed successfully' :
          'Something went wrong processing your verification';
    } else {
      alert('Verification request failed')
    }
  } catch (error) {
    alert('Error verifying sentiment:', error)
  }
}
</script>

<template>
  <div class="verification-container" :class="{ hidden: !submissionId }">
    <div v-if="!verificationProcessed" class="center">
      <p class="question">Is this sentiment review correct?</p>
      <div class="button-container">
        <button
            class="yes-button"
            @click="verifySentiment(true)"
        >
          Yes
        </button>
        <button
            class="no-button"
            @click="verifySentiment(false)"
        >
          No
        </button>
      </div>
    </div>
    <div v-else>
      <p class="status-message">
        {{ statusMessage }}
      </p>
    </div>
  </div>
</template>


<style scoped>
.hidden {
  visibility: hidden; /* hidden but takes up space */
}


.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.verification-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center; /* centers content vertically */
  text-align: center;

  padding: 20px;
  border: 2px solid #0056b3;
  border-radius: 12px;
  background-color: #f9f9f9;

  width: 20vw;
  min-height: 10vh; /* gives breathing room but still grows with content */
  margin: 20px auto;
}


.question {
  font-size: 1.2rem;
}

.button-container {
  display: flex;
  gap: 10px;
}

.yes-button, .no-button {
  padding: 10px 20px;
  font-size: 1rem;
  border: none;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.yes-button {
  background-color: green;
  color: white;
}

.yes-button:hover {
  background-color: #4caf50;
}

.no-button {
  background-color: red;
  color: white;
}

.no-button:hover {
  background-color: #f44336;
}
</style>
