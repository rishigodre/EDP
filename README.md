# EDP | CareSync

- The data from the hardware will be stored in chunks of T seconds into the SD card in a simple string format
  (can be changed anytime)
### Simple Data Formatting Scheme For Communication With The Server:
```
log -> hwid, hwpassword, payload,
payload -> (sensorID, timestamp, SensorData) * N, separated by '/n'
hwid -> string (uuid)
hwpassword -> string (16 chars)
sensorID -> string (1 digit, 0-9)
timestamp -> string (var char, unix timestamp, 13 digits)
sensorData -> string (var char, data separated by '|')
```
#### Alert
```
alert ->  hwid, hwpassword, timestamp, sensorID, alertMessage
hwid -> string (uuid)
hwpassword -> string (16 chars)
timestamp -> string (var char, unix timestamp, 13 digits)
sensorID -> string (1 digit, 0-9)
alertMessage -> string (var char, alert message)
```


## Start the Care Sync Server

.env:
```
DB_CONN_STRING=
DB_NAME=EDP
```

```bash
$ cd EDP
$ cd Server
$ npm i
$ npm start
```
## Start the Care Sync Client

```bash
$ cd EDP
$ cd Client
$ npm i
$ npm run dev
```


