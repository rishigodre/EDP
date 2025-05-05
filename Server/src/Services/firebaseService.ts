import { MongoDB } from "./database.service";
import { DeviceToken } from "../Models/deviceToken";
import path from "path";
import { Notification } from "../Models/notification"; 

var admin = require("firebase-admin");

const serviceAccount = require(path.join(__dirname, "../../../service_account.json"));

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

export async function sendNotification(title: string, body: string) {
  if (!MongoDB.db) throw new Error("Database not connected");

  const tokens = await MongoDB.db.collection<DeviceToken>("DeviceTokens").find({}).toArray();

  for (const token of tokens) {
    console.log(token.fcmToken);
    const message = {
      notification: { title, body },
      token: token.fcmToken,
    };

    try {
      await admin.messaging().send(message);
      console.log(`Notification sent to ${token.deviceId}`);

      const notification = new Notification(
        token.deviceId,
        title,
        body
      );

      await MongoDB.db.collection<Notification>("Notifications").insertOne(notification);
    } catch (error) {
      console.error(`Failed to send notification: ${error}`);
    }
  }
}