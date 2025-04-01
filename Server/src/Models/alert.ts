export class Alert{
    constructor(
        public hwid: string,
        public password: string,
        public timestamp: number,
        public sensorId: number,
        public info: string,
    ) { }
}

export class ClientMessage {
    constructor(
        public hwid: string,
        public password: string,
        public timestamp: number,
        public type: string
    ) { }
}