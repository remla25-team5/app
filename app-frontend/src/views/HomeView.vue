<script setup lang="ts">
import { ref } from 'vue';

// Reactive variable to store the input text
const text = ref('');

// Method to handle the submission of the review
const submitReview = () => {
  const apiUrl = import.meta.env.VITE_API_URL;

  console.log(apiUrl); // "https://api.example.com"
  console.log("Review Submitted:", text.value);
  // You can replace this with your actual submission logic (e.g., sending to an API)
  text.value = '';  // Clear the text box after submission
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
  </div>
</template>


<style scoped>
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
