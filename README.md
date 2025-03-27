# EDP | CareSync

- The data from the hardware will be stored in chunks of T seconds into the SD card in a simple string format
  (can be changed anytime)
### Simple Data Formatting Scheme:
```
chunk       -> version, uuid, data
data        -> uuid, timestamp, payload
payload     -> [ N ] : [ log ] * N
log         -> [ sensor_id ] , [ value ]
version     -> string
uuid        -> string
sensor_id   -> string
value       -> float
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


