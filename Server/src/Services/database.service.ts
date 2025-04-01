import * as dotenv from 'dotenv';
import * as mongoDB from "mongodb";

export const MongoDB : {db?: mongoDB.Db} = {};
export async function connectToDatabase() {
    dotenv.config();
    if (process.env.DB_CONN_STRING === undefined || process.env.DB_NAME === undefined) {
        throw new Error("Environment variables not set");
    }
    console.log(process.env.DB_CONN_STRING);
    const client: mongoDB.MongoClient = new mongoDB.MongoClient(process.env.DB_CONN_STRING);
    await client.connect();
    MongoDB.db = client.db(process.env.DB_NAME);
    console.log(`Successfully connected to database: ${MongoDB.db.databaseName}`);
}