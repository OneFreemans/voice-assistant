import requests
import config


class YandexSmartHome:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.iot.yandex.net/v1.0"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_devices(self):
        response = requests.get(
            f"{self.base_url}/user/info",
            headers=self.headers
        )

        print("=== DEBUG ===")
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Text: {response.text[:500]}")
        print("=============")

        if response.status_code == 200:
            try:
                return response.json()
            except:
                return {"error": "Не JSON", "text": response.text}
        else:
            return {"error": f"HTTP {response.status_code}", "text": response.text}

    def control_device(self, device_id, action="on", brightness=None):
        """
        action: 'on', 'off'
        brightness: 0-100 (для лампочек)
        """
        payload = {
            "devices": [
                {
                    "id": device_id,
                    "actions": []
                }
            ]
        }

        # Команда включения/выключения
        if action in ["on", "off"]:
            payload["devices"][0]["actions"].append({
                "type": "devices.capabilities.on_off",
                "state": {
                    "instance": "on",
                    "value": action == "on"
                }
            })

        # Яркость (если есть) не реализована в командах
        if brightness is not None:
            payload["devices"][0]["actions"].append({
                "type": "devices.capabilities.range",
                "state": {
                    "instance": "brightness",
                    "value": brightness
                }
            })

        response = requests.post(
            f"{self.base_url}/devices/actions",
            headers=self.headers,
            json=payload
        )
        return response.status_code, response.json()

    def run_scenario(self, scenario_id):
        """Запуск сценария"""
        response = requests.post(
            f"{self.base_url}/scenarios/{scenario_id}/actions",
            headers=self.headers,
            json={}
        )
        return response.status_code, response.json()