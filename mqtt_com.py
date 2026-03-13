import time
import random
import subprocess
import json
import psutil
import paho.mqtt.client as mqtt


BROKER = "192.168.110.12"
PORT = 1883
DEVICE_ID = random.randint(1000, 9999)
COMMAND_TOPIC = f"device/{DEVICE_ID}/commands"
METRICS_TOPIC = f"device/{DEVICE_ID}/metrics"


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected to: {DEVICE_ID}")
    client.subscribe(COMMAND_TOPIC)
    print(f"Subscribed on Topic: {COMMAND_TOPIC}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"New Command: {payload}")
    try:
        subprocess.run(payload, shell=True, check=True)
    except Exception as e:
        print(f"Error while Executing remote command: {e.__class__.__name__} {e}")

def get_metrics():
    return {
        "cpu_usage": psutil.cpu_percent(interval=None),
        "ram_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "boot_time": psutil.boot_time()
    }


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    try:
        metrics = get_metrics()
        client.publish(METRICS_TOPIC, json.dumps(metrics))
        time.sleep(3)
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
        break
    except Exception as e:
        print(f'Main Exception: {e.__class__.__name__} {e}')
        time.sleep(5)
