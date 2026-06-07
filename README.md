# Factory Floor Digital Twin

English | [Traditional Chinese](README.zh-TW.md)

Factory Floor Digital Twin is a demo project that visualizes a factory-floor digital twin with NVIDIA Omniverse Kit. The system generates simulated machine telemetry from ROS2, forwards the data through MQTT, and updates machine status, materials, HUD panels, alarm lists, the mini map, and machine labels inside a USD factory scene through a custom Omniverse extension.

## Demo Video

[![Industrial Digital Twin Demo](demo/demo-thumbnail.jpg)](https://youtu.be/GCUeru59X_M)

[Watch the full demo on YouTube](https://youtu.be/GCUeru59X_M)

## Highlights

- Real-time telemetry flow from ROS2 topics to MQTT and Omniverse Kit.
- Config-driven machine, topic, threshold, color, and USD prim path mapping.
- Omniverse extension updates USD machine materials based on operation mode and severity.
- HUD panel, alert list, factory overview, mini map, and viewport machine labels.
- Demo scene built on NVIDIA's official USD Explorer factory sample assets.

## Demo Scene Asset

This project uses NVIDIA's official [USD Explorer Sample Assets Pack](https://docs.omniverse.nvidia.com/usd/latest/usd_content_samples/downloadable_packs.html#usd-explorer-sample-assets-pack) as the demo factory scene.

Due to NVIDIA asset licensing restrictions, this repository does not include or redistribute the asset. To run the same scene, download the sample assets pack separately and open the following USD file in your Omniverse Kit app:

```text
USD_Explorer_Sample_NVD@10011\Usd_Explorer\Samples\Examples\2023_2\Factory\Factory.usd
```

The `usd_prim_path` values in `config/machines.toml` are configured for this factory sample scene. If you use a different USD scene, update the machine-to-prim mappings accordingly.

## Architecture Overview

```text
ROS2 Machine Publisher
  -> /factory/{machine_id}/{parameter}
  -> ROS2 to MQTT Bridge
  -> factory/{machine_id}/{parameter}
  -> Mosquitto MQTT Broker
  -> Omniverse Kit Extension
  -> USD prim material / HUD / minimap / machine labels
```

Core components:

- `ros2_publisher/`: Generates simulated machine telemetry, including temperature, vibration, and operation mode.
- `bridge/`: Forwards ROS2 topics to MQTT topics.
- `config/`: Shared machine, topic, threshold, color, and USD prim path configuration.
- `omniverse_extension/`: Omniverse Kit extension that subscribes to MQTT, computes machine states, and updates the USD scene and UI.
- `docker-compose.yml`: Starts the Mosquitto MQTT broker.

For more detailed architecture notes, see [docs/architecture.md](docs/architecture.md).

## Project Structure

```text
factory-floor-digital-twin/
├─ bridge/                 # ROS2 -> MQTT bridge
├─ config/                 # Machine, topic, threshold, and USD prim path configuration
├─ docs/                   # Additional architecture notes
├─ mosquitto/              # Mosquitto broker configuration
├─ omniverse_extension/    # Omniverse Kit Python extension
├─ ros2_publisher/         # ROS2 simulated telemetry generator
├─ docker-compose.yml
└─ README.md
```

## Prerequisites

This repository assumes that you already have your own Omniverse Kit App Template development environment. This README does not cover Kit App Template installation; it only explains how to connect this extension to an existing Kit app.

Recommended environment:

- Windows 10/11
- NVIDIA GPU and a driver environment capable of running Omniverse Kit SDK
- Docker Desktop
- WSL2 Ubuntu
- ROS2 Humble or a compatible version
- Python 3.10 or later
- Existing NVIDIA Omniverse Kit App Template project

The ROS2 publisher and bridge require:

```bash
pip install paho-mqtt
```

ROS2-related packages are usually provided by the ROS2 environment:

- `rclpy`
- `std_msgs`

The Omniverse extension also imports `paho.mqtt.client`. If the Kit app reports `No module named 'paho'` during startup, add `paho-mqtt` to your Kit App Template Python dependency flow, for example in `kit-app-template/tools/deps/pip.toml`, and rebuild the app.

## Connect to an Existing Kit App Template

First, clone this repository:

```powershell
cd <your-workspace>
git clone <this-repo-url> factory-floor-digital-twin
```

In your Kit App Template project, make the extension discoverable from `source/extensions`. On Windows, you can use a junction:

```powershell
cd <your-workspace>\kit-app-template
New-Item -ItemType Junction `
  -Path .\source\extensions\omni.factory.twin `
  -Target <your-workspace>\factory-floor-digital-twin\omniverse_extension
```

Then add the extension dependency to your Kit app `.kit` file:

```toml
[dependencies]
"omni.factory.twin" = {}
```

Also make sure the extension search path includes the Kit App Template `source/extensions` directory:

```toml
[settings.app.exts]
folders.'++' = [
    "${app}/../../../../source/extensions",
]
```

If your app was created manually, also make sure the Kit App Template build configuration includes the app:

```lua
-- premake5.lua
define_app("<your_app_name>.kit")
```

```toml
# repo.toml
[repo_precache_exts]
apps = ["${root}/source/apps/<your_app_name>.kit"]
```

## Run the Demo

### 1. Start the MQTT Broker

```powershell
cd <your-workspace>\factory-floor-digital-twin
docker compose up -d
```

### 2. Start the ROS2 Publisher

In a WSL2 / ROS2 terminal:

```bash
cd <factory-floor-digital-twin>
source /opt/ros/humble/setup.bash
python3 ros2_publisher/machine_publisher.py
```

### 3. Start the ROS2-to-MQTT Bridge

Open another WSL2 / ROS2 terminal:

```bash
cd <factory-floor-digital-twin>
source /opt/ros/humble/setup.bash
python3 bridge/ros2_to_mqtt.py
```

If the bridge cannot connect to the broker, adjust the broker host according to your Windows / WSL2 / Docker network setup:

```python
# bridge/ros2_to_mqtt_config.py
MQTT_BROKER_HOST = "<broker-host>"
MQTT_BROKER_PORT = 1883
```

The Omniverse extension currently connects to `localhost:1883` by default.

### 4. Start the Omniverse Kit App

Launch your existing app from the Kit App Template project:

```powershell
cd <your-workspace>\kit-app-template
.\repo.bat launch
```

After startup, verify that:

1. `Factory Floor Digital Twin` / `omni.factory.twin` is available and enabled in Extension Manager.
2. `USD_Explorer_Sample_NVD@10011\Usd_Explorer\Samples\Examples\2023_2\Factory\Factory.usd` is open.
3. The MQTT broker, ROS2 publisher, and ROS2-to-MQTT bridge are all running.
4. MQTT connect / subscribe / message logs appear in the Omniverse Console.

## Topics and Payload Format

ROS2 topic:

```text
/factory/{machine_id}/{parameter}
```

MQTT topic:

```text
factory/{machine_id}/{parameter}
```

Example payload:

```json
{"machine_id": "m_00", "temperature": 72.5}
```

```json
{"machine_id": "m_00", "operation_mode": "RUNNING"}
```

Supported parameters and states are mainly defined by `config/thresholds.toml`:

- `temperature`
- `vibration`
- `operation_mode`
- `RUNNING`
- `IDLE`
- `SHUTDOWN`
- `OFFLINE`

## Common Checks

- Extension cannot be loaded: Check the junction, `.kit` dependency, extension search path, and Kit App Template build settings.
- MQTT data is missing: Make sure the broker, publisher, and bridge are running, and check the broker host between WSL2 and Windows/Docker.
- USD prims do not change color: Make sure the current stage is the NVIDIA factory sample, or align the `usd_prim_path` values in `config/machines.toml` with your own USD scene.
- Kit app startup is slow: The app may be updating the extension cache or initializing RTX shaders. Later launches are usually faster.
