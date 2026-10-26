const express = require("express");
const cors = require("cors");
const { pool } = require("./db");
const { getClient } = require("./redisClient");

const app = express();
app.use(cors());

const CACHE_TTL_SECONDS = 300;

app.get("/api/recommendations/:userId", async (req, res) => {
  const { userId } = req.params;
  const cacheKey = `rec:user:${userId}`;
  try {
    const redis = await getClient();
    const cached = await redis.get(cacheKey);
    if (cached) return res.json({ source: "cache", recommendations: JSON.parse(cached) });

    const { rows } = await pool.query(
      "SELECT item_id, score, rank FROM recommendations WHERE user_id = $1 ORDER BY rank ASC",
      [userId]
    );
    await redis.setEx(cacheKey, CACHE_TTL_SECONDS, JSON.stringify(rows));
    res.json({ source: "db", recommendations: rows });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "failed to fetch recommendations" });
  }
});

app.get("/api/items/:itemId/similar", async (req, res) => {
  const { itemId } = req.params;
  const cacheKey = `sim:item:${itemId}`;
  try {
    const redis = await getClient();
    const cached = await redis.get(cacheKey);
    if (cached) return res.json({ source: "cache", similarItems: JSON.parse(cached) });

    const { rows } = await pool.query(
      "SELECT similar_item_id, similarity, rank FROM item_similarity WHERE item_id = $1 ORDER BY rank ASC",
      [itemId]
    );
    await redis.setEx(cacheKey, CACHE_TTL_SECONDS, JSON.stringify(rows));
    res.json({ source: "db", similarItems: rows });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "failed to fetch similar items" });
  }
});

app.get("/api/metrics", async (req, res) => {
  try {
    const { rows } = await pool.query(
      "SELECT DISTINCT ON (metric_name) metric_name, metric_value, computed_at FROM model_metrics ORDER BY metric_name, computed_at DESC"
    );
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "failed to fetch metrics" });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Serving API listening on :${PORT}`));
