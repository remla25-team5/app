const express = require('express');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(cors());
app.use(express.json());

// Mock database
const submissions = {};

// POST /submit
app.post('/submit', (req, res) => {
    const { text } = req.body;
    if (!text) return res.status(400).json({ error: 'Text is required' });

    const submissionId = uuidv4();
    const sentiment = Math.random() < 0.5; // Random true/false for mock

    submissions[submissionId] = { text, sentiment };
    res.json({ sentiment, submissionId });
});

// POST /verify
app.post('/verify', (req, res) => {
    const { submissionId, isCorrect } = req.body;
    if (!submissionId || typeof isCorrect !== 'boolean') {
        return res.status(400).json({ error: 'submissionId and isCorrect are required' });
    }

    if (!submissions[submissionId]) {
        return res.status(404).json({ error: 'Submission not found' });
    }

    // Optionally store or log verification
    console.log(`Verification for ${submissionId}: ${isCorrect}`);

    const verified = Math.random() < 0.5;

    res.json({ verified });
});

// GET /version/app
app.get('/version/app', (req, res) => {
    res.json({ version: '1.0.0' });
});

// GET /version/model
app.get('/version/model', (req, res) => {
    res.json({ modelVersion: '2025.04.01-ml-v5' });
});

// Start server
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Mock API server running at http://localhost:${PORT}`);
});
