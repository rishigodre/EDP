// External Dependencies
import express, { Request, Response } from "express";
import { connectToDatabase } from "../Services/database.service";
import { Chunk } from "../Models/chunk";
import { ParseAlert, ParseRawData } from "../Helpers/Parser";
import { MongoDB } from "../Services/database.service";
import * as mongoDB from "mongodb";
import { WebSocketService } from "../Services/websocket.service";
import { Alert } from "../Models/alert";
import { UserLog } from "../Models/userLog";
import { ObjectId } from "mongodb";
import { DeviceToken } from "../Models/deviceToken";
import { sendNotification } from "../Services/firebaseService";


export const router = express.Router();

const DB: { db?: mongoDB.Db } = MongoDB; // Assign the database connection to a variable
console.log("Database: ", DB.db?.databaseName);
router.use(express.text());
router.use(express.json());


const wss = new WebSocketService(3011);

// GET
router.get("/getallrawdata", async (_req: Request, res: Response) => {
    try {
        if (!DB.db) throw new Error("Database not connected");
        const chunks = await DB.db.collection<Chunk>("Chunks").find({}).toArray();
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

        const chunks = (await DB.db.collection<Chunk>("Chunks").find({ timestamp: { $gt: timestamp }, hwid: { $eq: hwid }, password: { $eq: password } }).sort({ timestamp: -1 }).toArray());
        res.status(200).send(chunks);
    } catch (ex: any) {
        res.status(500).send(ex.message);
    }
});

// POST
router.post("/addrawdata", async (req: Request, res: Response) => {
    try {
        const rawData: string = req.body;
        if (!rawData) throw new Error("No data provided");
        const parsedData = ParseRawData(rawData.trim());
        if (!DB.db) throw new Error("Database not connected");
        if (!wss.checkRunningStatus(parsedData.hwid + parsedData.password)) {   
            res.status(200).send("Device not enabled");
            return;
        }

        const result = await DB.db.collection<Chunk>("Chunks").insertOne(parsedData);

        if (!result.acknowledged) throw new Error("Failed to insert data into database");

        res.status(200).send({ message: "Data inserted successfully", id: result.insertedId });
    } catch (error: any) {
        res.status(500).send(error.message);
    }
});


router.post("/alert", async (req: Request, res: Response) => {
    try {
        const alertData = req.body;
        if (!alertData) throw new Error("No data provided");
        if (!DB.db) throw new Error("Database not connected");
        const alert: Alert = ParseAlert(alertData);
        sendNotification("Alert", alert.info);
        wss.broadcastToClient(alert);
        res.status(200).send({ message: "Alert sent successfully" });
    } catch (error: any) {
        res.status(500).send(error.message);
    }
});
// PUT

router.post("/userLog", async (req: Request, res: Response) => {
    try {
        if (!DB.db) throw new Error("Database not connected");

        const { sensorId, logMessage, userId, password } = req.body;

        if (sensorId === undefined || sensorId === null) throw new Error("No sensorId provided");
        if (!logMessage) throw new Error("No log message provided");

        const newLog = new UserLog(sensorId, logMessage, userId, password);

        const result = await DB.db.collection<UserLog>("UserLogs").insertOne(newLog);
        res.status(200).send('User log recorded successfully');
    } catch (error: any) {
        res.status(500).send(error.message);
    }
});


router.get("/userLog", async (req: Request, res: Response): Promise<any> => {
    try {
        if (!DB.db) throw new Error("Database not connected");

        const userId = req.query.userId as string;
        const password = req.query.password as string;

        if (!userId || !password) {
            return res.status(400).send("Invalid or missing credentials ");
        }

        const logs = await DB.db.collection<UserLog>("UserLogs").find({ userId, password }).sort({ timestamp: -1 }).toArray();

        res.status(200).send(logs);
    } catch (error: any) {
        res.status(500).send(error.message);
    }
});

router.delete("/userLog/:id", async (req: Request, res: Response): Promise<any> => {
    try {
        if (!DB.db) throw new Error("Database not connected");

        const { id } = req.params;
        const result = await DB.db.collection<UserLog>("UserLogs").deleteOne({ _id: new ObjectId(id) });

        if (result.deletedCount === 0) {
            return res.status(404).send("User log not found");
        }
        return res.status(200).send("User log deleted");
    } catch (error: any) {
        return res.status(500).send(error.message);
    }
});

router.post("/deviceToken", async (req: Request, res: Response): Promise<any> => {
    try {
        if (!DB.db) throw new Error("Database not connected");

        const { deviceId, fcmToken } = req.body;
        if (!deviceId || !fcmToken) {
            return res.status(400).send("Missing deviceId or fcmToken");
        }

        const result = await DB.db.collection<DeviceToken>("DeviceTokens").findOneAndUpdate(
            { deviceId },
            { $set: { fcmToken, createdAt: Date.now() } },
            { returnDocument: "after", upsert: true } // upsert inserts if not found
        );

        if (!result) {
            return res.status(500).send("Upsert failed, no document returned.");
        }

        return res.status(200).send({
            message: "Token saved"
        });
    } catch (error: any) {
        return res.status(500).send(error.message);
    }
});

router.get("/notifications", async (_req: Request, res: Response): Promise<any> => {
    try {
        if (!DB.db) throw new Error("Database not connected");

        const notifications = await DB.db.collection("Notifications").find({}).sort({ timestamp: -1 }).toArray();

        res.status(200).send(notifications);
    } catch (error: any) {
        res.status(500).send(error.message);
    }
});

// DELETE