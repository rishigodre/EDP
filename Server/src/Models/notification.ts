export class Notification {
    constructor(
        public deviceId: string,
        public notificationTitle: string,
        public notificationMessage: string,
        public timestamp: number = Date.now()
    ) {}
}