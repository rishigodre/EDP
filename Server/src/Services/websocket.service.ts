import { WebSocket, WebSocketServer } from "ws";
import { ParseClientMessage } from "../Helpers/Parser";
import { Alert } from "../Models/alert";

export const portwss: { port?: number } = {};

export class WebSocketService {
  private wss: WebSocketServer;
  private clients: Map<string, WebSocket> = new Map();
  private running: Map<string, boolean> = new Map();

  constructor(port: number) {
    this.wss = new WebSocketServer({ port , });

    this.wss.on("connection", (ws: WebSocket) => {
      console.log("New client connected");

      ws.on("message", (message) => {
        try {
          const msg = ParseClientMessage(message.toString());
          if (msg.type === "start") {
            this.running.set(msg.hwid + msg.password, true);
            console.log(`Client started with hwidpass: ${msg.hwid + msg.password}`);
          }
          if (msg.type === "stop") {
            this.running.set(msg.hwid + msg.password, false);
            console.log(`Client stopped with hwidpass: ${msg.hwid + msg.password}`);
          }
          if (msg.type === "register" && msg.hwid && msg.password) {
            this.clients.set(msg.hwid + msg.password, ws); // Register client by hwid
            console.log(`Client registered with hwidpass: ${msg.hwid + msg.password}`);
          }
        } catch (error) {
          console.error("Error parsing message:", error);
        }
      });

      // Handle client disconnection
      ws.on("close", () => {
        console.log("Client disconnected");
        this.removeClient(ws);
      });

      ws.on("error", (error) => {
        console.error("WebSocket error:", error);
        this.removeClient(ws);
      });
    });

    console.log(`WebSocket server started on port: ${port}`);
  }

  public checkRunningStatus(hwidpass: string): boolean{
    const flag = this.running.get(hwidpass);
    if (flag) {
      return flag;
    }
    return false;
  }

  private removeClient(ws: WebSocket): void {
    for (const [hwidpass, client] of this.clients.entries()) {
      if (client === ws) {
        this.clients.delete(hwidpass);
        console.log(`Client with hwidpass ${hwidpass} removed`);
        break;
      }
    }
  }

  public broadcastToClient(alert: Alert): void {
    const client = this.clients.get(alert.hwid + alert.password);
    if (client && client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(alert));
    } else {
      console.warn(`Client with hwidpass ${alert.hwid + alert.password} not connected`);
    }
  }
}

// Export a singleton instance
// export const websocketService = new WebSocketService(3001);