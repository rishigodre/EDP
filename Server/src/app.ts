import express from "express";
import { connectToDatabase } from "./Services/database.service"
import { router } from "./Routes/server.router";

const app = express();
const port = 3000;

connectToDatabase()
    .then(() => {
        app.use("/api", router);

        app.listen(port, () => {
            console.log(`Server started at http://localhost:${port}`);
        });
    })
    .catch((error: Error) => {
        console.error("Database connection failed", error);
        process.exit();
    });
