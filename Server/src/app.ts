import express from 'express';
const app = express();
const port = 3000;

app.get('/test', (req, res) => {
    res.send('Hello World!, server working just fine');
});


//Data format:
// [version]:[hwid]:[datasize]:[data]
// hwid: Hardware ID, a unique identifier for the device
// datasize: The size of the data in string length
// data: The data to be stored
// data -> :[sensor:id]:[value]):*

app.post('/postDataChunk', (req, res) => {
    const data = req.query.data;
    console.log(data);
});

app.get('/getDataChunk', (req, res) => {
    const hwid = req.query.hwid;
    console.log(hwid);
    res.send('Hello World!');
});

app.listen(port, () => {
    return console.log(`Express is listening at http://localhost:${port}`);
});