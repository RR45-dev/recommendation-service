const { createClient } = require("redis");

const client = createClient({ url: process.env.REDIS_URL || "redis://localhost:6379" });
client.on("error", (err) => console.error("Redis error", err));

async function getClient() {
  if (!client.isOpen) await client.connect();
  return client;
}

module.exports = { getClient };
