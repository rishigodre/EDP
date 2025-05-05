export class UserLog {
    constructor(
      public sensorId: number,
      public logMessage: string,
      public userId: string,
      public password: string,
      public timestamp: number = Date.now()
    ) {}
  }
