export class DeviceToken {
  constructor(
    public deviceId: string,
    public fcmToken: string,
    public createdAt: number = Date.now()
  ) {}
}