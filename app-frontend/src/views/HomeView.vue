<script setup lang="ts">
import { ref, computed } from 'vue';

// Reactive variable to store the input text
const text = ref('');
// Reactive boolean | null ref
const sentiment = ref<boolean | null>(null)

const face = computed(() => {
  if (sentiment.value === true) return '😄'
  if (sentiment.value === false) return '😞'
  return '😐'
})

const colorClass = computed(() => {
  if (sentiment.value === true) return 'green'
  if (sentiment.value === false) return 'red'
  return 'gray'
})

const message = computed(() => {
  if (sentiment.value === true) return 'Sentiment of your review is positive.'
  if (sentiment.value === false) return 'Sentiment of your review is negative.'
  return 'Submit a review for sentiment analysis!'
})


const submissionId = ref('');

// Method to handle the submission of the review
const submitReview = async () => {
  const apiUrl = import.meta.env.VITE_API_URL; // e.g., http://localhost:3000
  const endpoint = `${apiUrl}/submit`;

  if (!text.value.trim()) {
    console.warn('No text entered');
    return;
  }

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text: text.value })
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const result = await response.json();
    console.log('Review Submitted:', text.value);
    console.log('Result:', result);
    console.log('Sentiment:', result.sentiment);
    console.log('submissionId:', result.submissionId);
    sentiment.value = result.sentiment;
    submissionId.value = result.submissionId;


    text.value = '';  // Clear the text box after successful submission
  } catch (error) {
    console.error('Error submitting review:', error);
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
  height: 30vh; /* Set a fixed height */
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
.green {
  color: green;
}
.red {
  color: red;
}
.gray {
  color: gray;
}

.container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 90vh;
  padding: 20px;
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
</style>
