import { Double, Long, ObjectId } from "mongodb";

export class SensorData {
    constructor(
        public sensorId: number,
        public data: SensorLog[],
        ) { }
}

export class SensorLog {
    constructor(
        public timestamp: number,
        public data: number[],
    ) { }
}

export function GenerateEmptySensorData(): SensorData[] {
    let temp: SensorData[] = [];
    for (let i = 0; i < 6; i++) {
        temp.push(new SensorData(i, []));
    }
    return temp;
}