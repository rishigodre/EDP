import {describe, expect, test} from '@jest/globals';
import { ParseRawData } from "../src/Services/Parser";
import { Chunk } from "../src/Models/chunk";
const Data: string = "9334de0b9ebd424d95e40d338953137ef75c2a1d9e8b6c340174343583290467.056-55.23-233.24\n2174343594128113-124-23.32\n3174343596352523\n317434360989466678";
const CorrectChunk: Chunk = new Chunk(
    "9334de0b9ebd424d95e40d338953137e", Date.now(), "f75c2a1d9e8b6c34", [
    { sensorId: 0, data: [{ timestamp: 1743435832904, data: [67.056, 55.23, 233.24] }] },
    { sensorId: 1, data: []},
    { sensorId: 2, data: [{ timestamp: 1743435941281, data: [ 13, 124, 23.32] }] },
    { sensorId: 3, data: [
        { timestamp: 1743435963525, data: [ 23 ] },
        { timestamp: 1743436098946, data: [ 6678]}
    ]}
]);

test("Parse Raw Data", async () => {
    const parsedData = await ParseRawData(Data);
    parsedData.timestamp = CorrectChunk.timestamp;
    expect(JSON.stringify(parsedData)).toEqual(JSON.stringify(CorrectChunk));
});

