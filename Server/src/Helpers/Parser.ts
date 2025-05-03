import { Alert, ClientMessage } from "../Models/alert";
import { Chunk } from "../Models/chunk";
import { SensorLog, SensorData, GenerateEmptySensorData } from "../Models/sensorData";


export function ParseRawData(data: string): Chunk {
    try {
        const hwid = data.substring(0, 32);
        const hwpassword = data.substring(32, 48);
        const payload = data.substring(48);
        const lines = payload.split("\n");
        const sensorData: SensorData[] = GenerateEmptySensorData();

        lines.forEach(line => {
            if (line.length < 1) return;
            const sensorId = line.substring(0, 1);
            const timestamp = line.substring(1, 14);
            const sensorDataLine = line.substring(14).split("-");
            const log: SensorLog = new SensorLog(parseInt(timestamp), []);
            for (let i = 0; i < sensorDataLine.length; i++) {
                const sensorValue = parseFloat(sensorDataLine[i]);
                log.data.push(sensorValue);
            }
            sensorData[parseInt(sensorId)].data.push(log);
        });

        const chunk: Chunk = new Chunk(hwid, Date.now(), hwpassword, sensorData);
        return chunk;
    } catch (error) {
        throw new Error("Error processing raw data: " + error);
    }
}

export function ParseAlert(alert: string): Alert {
    try {
        return new Alert(
            alert.substring(0, 32), // hwid
            alert.substring(32, 48), // hwpassword
            parseInt(alert.substring(48, 61)), // timestamp
            parseInt(alert.substring(61, 62)), // sensorId
            alert.substring(62),
        );
    } catch (error) {
        throw new Error("Error processing alert: " + error);
    }
}

export function ParseClientMessage(message: string): ClientMessage {
    try { 
        return new ClientMessage(
            message.substring(0, 32), // hwid
            message.substring(32, 48), // hwpassword
            parseInt(message.substring(48, 61)), // timestamp
            message.substring(61), // type
        );
    } catch (error) {
        throw new Error("Error processing client message: " + error);
    }
}