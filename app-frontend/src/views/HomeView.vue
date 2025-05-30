<script setup lang="ts">
import { ref, computed } from 'vue';
import Verify from "@/components/Verify.vue";
import Version from "@/components/Version.vue";
import axios from "axios";

// Use environment variables for API base URL
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
// const apiBaseUrl = 'http://localhost:8080/api';

const text = ref('');
const sentiment = ref<string | null>(null)

const face = computed(() => {
  if (sentiment.value === "positive") return '😄'
  if (sentiment.value === "negative") return '😞'
  if (sentiment.value === "neutral") return '😐'
  return '🤔'
})

const colorClass = computed(() => {
  if (sentiment.value === "positive") return 'green'
  if (sentiment.value === "positive") return 'red'
  if (sentiment.value === "neutral") return 'yellow'
  return 'gray'
})

const message = computed(() => {
  if (sentiment.value === "positive") return 'Sentiment of your review is positive.'
  if (sentiment.value === "negative") return 'Sentiment of your review is negative.'
  if (sentiment.value === "neutral") return 'Sentiment of your review is neutral.'
  return 'Submit a review for sentiment analysis!'
})


const submissionId = ref('');

// Method to handle the submission of the review
const submitReview = async () => {
  const endpoint = `${apiBaseUrl}/submit`;

  if (!text.value.trim()) {
    alert('Submitting empty review not allowed');
    return;
  }

  try {
    const { data } = await axios.post(endpoint, { text: text.value });

    console.log('Review Submitted:', text.value);
    console.log('Result:', data);
    console.log('Sentiment_label:', data.sentiment_label);
    console.log('submissionId:', data.submissionId);

    sentiment.value = data.sentiment_label;
    submissionId.value = data.submissionId;
    // text.value = '';
  } catch (error) {
    // Show the error message returned from the backend
    alert(`Error while submitting review: ${error}`);
    console.log(`Error while submitting review: ${error}`);
  }
};

</script>

<template>
  <div class="container">
    <h2 class="title">Write your review</h2>
    <textarea
        v-model="text"
        class="text-box"
        placeholder="Start typing here..."
        rows="10"
        cols="50"
    ></textarea>
    <button @click="submitReview" class="submit-btn">Submit</button>
    <div class="sentiment-container">
      <p class="message">{{ message }}</p>
      <div :class="['emoji', colorClass]">{{ face }}</div>
    </div>
    <Verify :submissionId="submissionId"></Verify>
    <Version></Version>
  </div>

</template>


<style scoped>
.sentiment-container {
  display: flex;
  flex-direction: column;
  align-items: center; /* centers horizontally */
  justify-content: center; /* centers vertically */
  text-align: center;
  width: 35vw; /* Set a fixed width */
  height: 35vh; /* Set a fixed height */
  border: 2px solid #0056b3; /* Blue border */
  border-radius: 12px; /* Rounded corners */
  margin: 20px auto; /* Center the container with space around it */
  padding: 20px; /* Inner space to prevent content touching the border */
  background-color: #f9f9f9; /* Light background color */
  box-sizing: border-box; /* Include padding and border in width/height */
  overflow: hidden; /* Prevent content overflow */
}

.message {
  font-size: 1.8rem;
  margin-top: 1rem;
}


.emoji {
  font-size: 4rem;
}

.container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 80vh;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.text-box {
  width: 80%;
  padding: 10px;
  font-size: 16px;
  line-height: 1.5;
  border: 1px solid #ccc;
  border-radius: 5px;
  resize: none;
  margin-bottom: 20px;
}

.text-box:focus {
  border-color: #007bff;
  outline: none;
}

.submit-btn {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.submit-btn:hover {
  background-color: #0056b3;
}

.green {
  color: #4CAF50;
}

.red {
  color: #F44336;
}

.gray {
  color: #9E9E9E;
}
</style>
