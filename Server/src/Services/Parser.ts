import { Chunk } from "../Models/chunk";
import { SensorLog, SensorData, GenerateEmptySensorData} from "../Models/sensorData";


export function ParseRawData(data : string): Chunk {
    try {
        //take the hwid
        const hwid = data.substring(0, 32);
        const hwpassword = data.substring(32, 48);
        const payload = data.substring(48);
        const lines = payload.split("\n");
        const sensorData: SensorData[] = GenerateEmptySensorData();
        console.log("Sensor Data: ", sensorData);
        lines.forEach(line => {
            const sensorId = line.substring(0, 1);
            const timestamp = line.substring(1, 14);
            const sensorDataLine = line.substring(14).split("-");
            const log: SensorLog = new SensorLog(parseInt(timestamp), []);
            for (let i = 0; i < sensorDataLine.length; i++) {
                const sensorValue = parseFloat(sensorDataLine[i]);
                log.data.push(sensorValue);
            }
            console.log("Sensor ID: ", sensorId);
            console.log("Sensor Log: ", log);
            //push the log to the sensor data
            sensorData[parseInt(sensorId)].data.push(log);
        }); 
        //create the chunk object
        const chunk: Chunk = new Chunk(hwid, Date.now(), hwpassword, sensorData);
        return chunk;
    } catch (error) {
        console.error("Error processing chunk:", error);
        return new Chunk("", 0, "", []);
    }
}