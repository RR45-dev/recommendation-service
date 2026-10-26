const { Pool } = require("pg");

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || "postgresql://recadmin:recadmin@localhost:5432/recsys",
});

module.exports = { pool };
