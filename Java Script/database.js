const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bcrypt = require('bcrypt');

class Database {
    constructor() {
        const dbPath = path.resolve(__dirname, '..', 'phishshield.db');
        this.db = new sqlite3.Database(dbPath, (err) => {
            if (err) {
                console.error('Database connection error:', err.message);
            }
            console.log('Connected to the PhishShield database.');
        });
    }

    initializeDatabase() {
        this.db.serialize(() => {
            this.db.run(`
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    password TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            `);
        });
    }

    async registerUser(username, email, phone, password) {
        return new Promise((resolve, reject) => {
            this.db.get('SELECT * FROM users WHERE email = ?', [email], async (err, row) => {
                if (err) {
                    return reject(err);
                }
                
                if (row) {
                    return reject(new Error('User already exists'));
                }

                const saltRounds = 10;
                try {
                    const hashedPassword = await bcrypt.hash(password, saltRounds);

                    const stmt = this.db.prepare('INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)');
                    stmt.run(username, email, phone, hashedPassword, function(err) {
                        if (err) {
                            return reject(err);
                        }
                        resolve({ id: this.lastID, username, email });
                    });
                    stmt.finalize();
                } catch (hashErr) {
                    reject(hashErr);
                }
            });
        });
    }

    async loginUser(email, password) {
        return new Promise((resolve, reject) => {
            this.db.get('SELECT * FROM users WHERE email = ?', [email], async (err, user) => {
                if (err) {
                    return reject(err);
                }
                
                if (!user) {
                    return reject(new Error('User not found'));
                }

                const isMatch = await bcrypt.compare(password, user.password);
                
                if (!isMatch) {
                    return reject(new Error('Invalid credentials'));
                }

                resolve(user);
            });
        });
    }

    close() {
        this.db.close((err) => {
            if (err) {
                console.error(err.message);
            }
            console.log('Closed the database connection.');
        });
    }
}

module.exports = new Database();