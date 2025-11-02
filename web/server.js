const express = require('express');
const mysql = require('mysql2/promise');

const app = express();
app.use(express.static('public'));

const DB = {
  host: process.env.MYSQL_HOST || 'mysql',
  user: process.env.MYSQL_USER || 'root',
  password: process.env.MYSQL_PWD || 'root',
  database: 'alerts'
};

app.get('/events', async (req, res) => {
  res.set({
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive'
  });
  res.flushHeaders();

  let lastHash = '';
  const pool = await mysql.createPool(DB);

  const timer = setInterval(async () => {
    try {
      const [rows] = await pool.query("SELECT * FROM suspicious_transactions ORDER BY ts_utc DESC LIMIT 100");
      const payload = JSON.stringify(rows);
      if (payload !== lastHash) {
        lastHash = payload;
        res.write(`event: update\n`);
        res.write(`data: ${payload}\n\n`);
      }
    } catch (e) { /* ignore */ }
  }, 2000);

  req.on('close', () => clearInterval(timer));
});

app.listen(3000, () => console.log('web listening on 3000'));
