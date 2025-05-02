import { MongoDB } from "./database.service";
import { Chunk } from "../Models/chunk";

function createRandomPayload() {
    const payload = [];
    for (let sensorId = 0; sensorId < 4; sensorId++) {
      payload.push({
        sensorId,
        data: [
          {
            timestamp: Date.now(),
            data: Array.from({ length: 5 }, () => Math.random() * 100),
          },
        ],
      });
    }
    return payload;
  }

function insertMockData() {
  if (!MongoDB.db) return;
  const mockData: Chunk = {
    hwid: "mock-hwid",
    timestamp: Date.now(),
    password: "mock-pass",
    payload: createRandomPayload()
  };
  MongoDB.db.collection<Chunk>("Chunks").insertOne(mockData)
    .then(() => console.log("Inserted mock data"))
    .catch(err => console.error("Insertion error:", err));
}

export function scheduleMockData() {
  const nextDelay = 10000;
  setTimeout(() => {
    insertMockData();
    scheduleMockData();
  }, nextDelay);
}