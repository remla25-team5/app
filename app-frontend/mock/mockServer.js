const express = require('express');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(cors());
app.use(express.json());

// Middleware to log all incoming requests
app.use((req, res, next) => {
    console.log(`Incoming request: ${req.method} ${req.path}`);
    next();
});

// Mock database
const submissions = {};

// POST /api/submit
app.post('/api/submit', (req, res) => {
    const { text } = req.body;
    if (!text) return res.status(400).json({ error: 'Text is required' });

    const submissionId = uuidv4();
    const options = ["positive", "negative", "neutral"];
    const sentiment_label = options[Math.floor(Math.random() * options.length)];

    submissions[submissionId] = { text, sentiment_label };
    res.json({ sentiment_label, submissionId });
});

// POST /api/verify
app.post('/api/verify', (req, res) => {
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

// GET /api/version/app
app.get('/api/version/app', (req, res) => {
    res.json({ version: '1.0.0' });
});

// GET /api/version/model
app.get('/api/version/model', (req, res) => {
    res.json({ modelVersion: '2025.04.01-ml-v5' });
});

// Start server
const PORT = 8080;
app.listen(PORT, () => {
    console.log(`Mock API server running at http://localhost:${PORT}`);
    console.log('Available endpoints:');
    console.log(`  POST   http://localhost:${PORT}/api/submit`);
    console.log(`  POST   http://localhost:${PORT}/api/verify`);
    console.log(`  GET    http://localhost:${PORT}/api/version/app`);
    console.log(`  GET    http://localhost:${PORT}/api/version/model`);
});
