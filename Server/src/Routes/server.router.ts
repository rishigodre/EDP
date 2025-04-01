// External Dependencies
import express, { raw, Request, Response } from "express";
import { connectToDatabase } from "../Services/database.service";
import { Chunk } from "../Models/chunk";
import { ParseAlert, ParseRawData } from "../Helpers/Parser";
import { MongoDB } from "../Services/database.service";
import * as mongoDB from "mongodb";
import { WebSocketService } from "../Services/websocket.service";
import { Alert } from "../Models/alert";


export const router = express.Router();

const DB: { db?: mongoDB.Db } = MongoDB; // Assign the database connection to a variable
console.log("Database: ", DB.db?.databaseName);
router.use(express.json());

const wss = new WebSocketService(3010);

// GET
router.get("/getallrawdata", async (_req: Request, res: Response) => {
    try {
        if (!DB.db) throw new Error("Database not connected");
        const chunks = await DB.db.collection<Chunk>("Chunk").find({}).toArray();
        res.status(200).send(chunks);
    } catch (error: any) {
        res.status(500).send(error.message);
    }
});

router.get("/getrawdataafter", async (req: Request, res: Response) => {
    try {
        const timestamp = parseInt(req.query.timestamp as string);
        const hwid = req.query.hwid as string;
        const password = req.query.password as string;

        if (!timestamp) throw new Error("No timestamp provided");
        if (!DB.db) throw new Error("Database not connected");

        const chunks = (await DB.db.collection<Chunk>("Chunks").find({ timestamp: { $gt: timestamp }, hwid: { $eq: hwid }, password: { $eq: password } }).toArray());
        res.status(200).send(chunks);
    } catch (ex: any) {
        res.status(500).send(ex.message);
    }
});

// POST
router.post("/addrawdata", async (req: Request, res: Response) => {
    try {
        const rawData: string = req.body.Data;
        if (!rawData) throw new Error("No data provided");

        const parsedData = ParseRawData(rawData);
        if (!DB.db) throw new Error("Database not connected");

        const result = await DB.db.collection<Chunk>("Chunks").insertOne(parsedData);

        if (!result.acknowledged) throw new Error("Failed to insert data into database");

        res.status(200).send({ message: "Data inserted successfully", id: result.insertedId });
    } catch (error: any) {
        res.status(500).send(error.message);
    }
});

router.post("/alert", async (req: Request, res: Response) => {
    try {
        const alertData = req.body.Data;
        if (!alertData) throw new Error("No data provided");
        if (!DB.db) throw new Error("Database not connected");

        const alert: Alert = ParseAlert(alertData);
        console.log(alert);
        wss.broadcastToClient(alert);
        res.status(200).send({ message: "Alert sent successfully" });
    } catch (error: any) {
        res.status(500).send(error.message);
    }
});
// PUT

// DELETE