const express = require('express');
const cors = require('cors');
const path = require('path');
const bodyParser = require('body-parser');
const database = require('./database');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname, '..')));

// Initialize database
database.initializeDatabase();

// Routes will be added here later

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});



