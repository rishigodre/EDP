// External dependencies
import { ObjectId } from "mongodb";
import { SensorData } from "./sensorData";
// Class Implementation


export class Chunk {
    constructor(
        public hwid: string,
        public timestamp: number,
        public password: string,
        public payload: SensorData[],
    ) { }
}
