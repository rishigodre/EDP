import { Alert } from "../Models/alert";

export const  alerts : Alert[] = [];

export function CheckAlerts(hwid: string, password: string) {
    const alertList: Alert[] = [];
    alerts.forEach((alert, index) => {
        if (alert.hwid == hwid && alert.password == password) {
            alertList.push(alert);
            alerts.splice(index);
        }
    });
    return alertList;
}

export function SetAlert(alert : Alert ) {
    alerts.push(alert);
}