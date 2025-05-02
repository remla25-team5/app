# Vue 3 Project with Mock Server

This project is a Vue 3 application that uses a mock server to serve mock responses during development. Follow the instructions below to set up and run the project locally.

## Prerequisites

Make sure you have **Node.js** and **npm** installed. You can verify the installation by running the following commands in your terminal:

```bash
node -v
npm -v
```

## Installation

1. Clone the repository to your local machine:

```bash
git clone git@github.com:remla25-team5/app.git
cd app/app-frontend
```

2. Install dependencies:

```bash
npm install
```

## Running the Development Server

To start the development server with the mock API:

```bash
npm run dev
```

This will start both the Vue application and the mock server. The Vue application typically runs on `http://localhost:5173` (or another port if 5173 is already in use).

## Building for Production

To build the application for production:

```bash
npm run build
```

This will generate optimized production files in the `dist` directory which can be deployed to a web server.

