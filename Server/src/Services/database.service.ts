import * as dotenv from 'dotenv';
import * as mongoDB from "mongodb";

export const collections: { chunks?: mongoDB.Collection } = {}

export async function connectToDatabase() {
    dotenv.config();
    if (process.env.DB_CONN_STRING === undefined || process.env.DB_NAME === undefined) {
        throw new Error("Environment variables not set");
    }
    console.log(process.env.DB_CONN_STRING);
    const client: mongoDB.MongoClient = new mongoDB.MongoClient(process.env.DB_CONN_STRING);
    client.connect();
    const db: mongoDB.Db = client.db(process.env.DB_NAME);
    const chunksCollection = db.collection("chunks");
    collections.chunks = chunksCollection
    console.log(`Successfully connected to database: ${db.databaseName}`);
    return db;
}