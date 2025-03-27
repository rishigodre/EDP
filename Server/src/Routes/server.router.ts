// External Dependencies
import express, { Request, Response } from "express";
import { collections } from "../Services/database.service";
import Chunk from "../Models/chunk";


// Global Config
export const router = express.Router();
router.use(express.json());

// GET
router.get("/getalldata", async (_req: Request, res: Response) => {
    try {
        if(!collections.chunks) throw new Error("Database not connected");
        const games = (await collections.chunks.find({}).toArray()).map((chunk) => new Chunk(chunk.data, chunk._id));

        res.status(200).send(games);
    } catch (error: any) {
        res.status(500).send(error.message);
    }
});

// POST
router.post("/addchunk", async (req: Request, res: Response) => {
    try {
        if (!collections.chunks) throw new Error("Database not connected");
        const chunk = new Chunk(req.body.data);
        const result = await collections.chunks.insertOne(chunk);
        res.status(201).send(result.insertedId);
    } catch (error: any) {
        res.status(500).send(error.message);
    }
});

// PUT

// DELETE