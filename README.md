# Factory Floor Digital Twin

Factory Floor Digital Twin 是一個以 NVIDIA Omniverse Kit 為前端的工廠數位分身練習專案。專案會從 ROS2 產生模擬機台狀態，透過 MQTT broker 轉送資料，最後由 Omniverse extension 訂閱 MQTT topic，更新 USD 場景中的機台顏色、HUD、告警清單、小地圖與機台標籤。

## 系統架構

```text
ROS2 Machine Publisher
  -> /factory/{machine_id}/{parameter}
  -> ROS2 to MQTT Bridge
  -> factory/{machine_id}/{parameter}
  -> Mosquitto MQTT Broker
  -> Omniverse Kit Extension
  -> USD prim material / HUD / minimap / machine labels
```

主要資料流如下：

1. `ros2_publisher/machine_publisher.py` 依照 `config/` 內的機台與門檻設定，每秒發布模擬感測資料。
2. `bridge/ros2_to_mqtt.py` 訂閱 ROS2 topic，將 JSON payload 發布到 MQTT topic。
3. `docker-compose.yml` 啟動本機 Mosquitto broker，預設監聽 `1883`。
4. `omniverse_extension/omniverse_factory_twin/` 在 Omniverse Kit 中啟動後，訂閱 `factory/#`，解析資料並更新場景與 UI。

## 專案結構

```text
factory-floor-digital-twin/
├─ bridge/                         # ROS2 -> MQTT bridge
├─ config/                         # 機台、topic、門檻與顏色設定
├─ docs/                           # 補充架構文件
├─ mosquitto/                      # Mosquitto broker 設定
├─ omniverse_extension/             # Omniverse Kit Python extension
│  ├─ config/extension.toml         # Extension metadata
│  ├─ omniverse_factory_twin/       # Extension 主體、model、view、MQTT client
│  └─ tool/                         # Omniverse / USD 輔助工具
├─ ros2_publisher/                 # ROS2 模擬資料產生器
├─ docker-compose.yml              # MQTT broker 啟動設定
└─ README.md
```

## 核心模組

### `config/`

- `machines.toml`：定義機台 ID、顯示名稱、對應 USD prim path 與區域。
- `thresholds.toml`：定義 `temperature`、`vibration`、`operation_mode` 的門檻、顏色與透明度。
- `topic_resolver.py`：統一產生 ROS2 topic、MQTT topic 與 MQTT subscribe pattern。
- `config_loader.py`：讀取 TOML 設定，提供 extension、publisher、bridge 共用的設定 API。

### `ros2_publisher/`

- `machine_publisher.py`：ROS2 node，定期發布每台機器的 `temperature`、`vibration`、`operation_mode`。
- `topic_data_generator.py`：管理機台狀態與腳本化運轉模式。
- `data_generate_base.py`、`data_generate_implement.py`：感測資料趨勢、雜訊與異常模擬。

### `bridge/`

- `ros2_to_mqtt.py`：ROS2 subscription 與 MQTT publish 的橋接程式。
- `ros2_to_mqtt_config.py`：MQTT broker host 與 port。若 bridge 在 WSL2 中執行、broker 在 Windows Docker 中執行，可能需要使用 Windows host IP。

### `omniverse_extension/`

- `config/extension.toml`：extension package 名稱為 `Factory Floor Digital Twin`，Python module 為 `omniverse_factory_twin`。
- `extension.py`：extension 入口，初始化 HUD、小地圖、機台標籤、material/collection 與 MQTT subscription。
- `base_extension.py`：處理 Omniverse extension lifecycle 與 MQTT polling。
- `mqtt_client.py`：以 `paho-mqtt` 連線 MQTT broker，將訊息放入 queue 供 Kit update loop 消化。
- `prim_render_manager.py`：建立狀態 material，並依機台狀態套用到對應 USD prim collection。
- `model/`：管理機台狀態、嚴重度、顏色、工廠 layout 與 overview 資料。
- `view/`：HUD、告警清單、機台資訊列表、小地圖與 label UI。

## 環境需求

建議開發環境：

- Windows 10/11
- NVIDIA GPU 與可執行 Omniverse Kit SDK 的驅動環境
- Git 與 Git LFS
- Docker Desktop
- WSL2 Ubuntu
- ROS2 Humble 或相容版本
- Python 3.10 以上
- NVIDIA Omniverse Kit App Template

本專案的 Omniverse extension 不是獨立 executable。它需要放進 Kit App Template 產生的 Kit app 裡執行。

## USD 範例資產

Demo 場景直接使用 NVIDIA Omniverse 官方的 [USD Explorer Sample Assets Pack](https://docs.omniverse.nvidia.com/usd/latest/usd_content_samples/downloadable_packs.html#usd-explorer-sample-assets-pack)。因為 NVIDIA asset 授權限制，本 repo 不會重新散布或內含這份資產。

如果想使用相同的展示場景，請自行從 NVIDIA 官方文件下載 sample assets pack，並在 Omniverse Kit app 中開啟：

```text
USD_Explorer_Sample_NVD@10011\Usd_Explorer\Samples\Examples\2023_2\Factory\Factory.usd
```

`config/machines.toml` 內的 `usd_prim_path` 是依這個 factory sample scene 設定的；如果改用其他 USD 場景，需要同步調整機台對應的 prim path。

## 接入既有 Kit App Template

本專案假設你已經有可執行的 Kit App Template 專案與既有 Kit app。請先 clone 本 repo，實際路徑依自己的環境調整：

```powershell
cd <your-workspace>
git clone <this-repo-url> factory-floor-digital-twin
```

Kit App Template 需要能在 `source/extensions` 找到本專案的 extension。建議用 junction 連結，避免複製後兩邊不同步：

```powershell
cd <your-workspace>\kit-app-template
New-Item -ItemType Junction `
  -Path .\source\extensions\omni.factory.twin `
  -Target <your-workspace>\factory-floor-digital-twin\omniverse_extension
```

接著確認 Kit app 的 `.kit` 檔案有載入 extension。以 `source/apps/guan_omniverse_practice.my_editor.kit` 為例：

```toml
[dependencies]
"omni.factory.twin" = {}

[settings.app.exts]
folders.'++' = [
    "${app}/../../../../source/extensions",
]
```

若 app 是手動建立，還需要確認 Kit App Template 的 build 設定有包含 app：

```lua
-- premake5.lua
define_app("guan_omniverse_practice.my_editor.kit")
```

```toml
# repo.toml
[repo_precache_exts]
apps = ["${root}/source/apps/guan_omniverse_practice.my_editor.kit"]
```

這三個設定是讓 Kit App Template 能找到並啟動本專案 extension 的關鍵變更。請依自己建立的 app 名稱與路徑調整。

## Python 套件

ROS2 publisher 與 bridge 需要：

```bash
pip install paho-mqtt
```

ROS2 相關套件通常由 ROS2 環境提供：

- `rclpy`
- `std_msgs`

Omniverse extension 端也會 import `paho.mqtt.client`。如果 Kit app 啟動時出現 `No module named 'paho'`，需要把 `paho-mqtt` 安裝到 Kit App Template 使用的 Python/pip dependency 流程中。最穩定的方式是在 `kit-app-template/tools/deps/pip.toml` 加入 `paho-mqtt`，然後重新 build。

範例：

```toml
[[dependency]]
python = "../../_build/target-deps/python"
packages = ["paho-mqtt"]
target = "../../_build/target-deps/pip_prebundle"
platforms = ["*"]
download_only = false
append_to_install_folder = true
python_include_dir = true
```

修改後執行：

```powershell
cd <your-workspace>\kit-app-template
.\repo.bat build
```

## 啟動流程

### 1. 啟動 MQTT broker

在本 repo 根目錄執行：

```powershell
cd <your-workspace>\factory-floor-digital-twin
docker compose up -d
```

確認 broker 狀態：

```powershell
docker ps --filter name=factory_mosquitto
```

### 2. 啟動 ROS2 publisher

在 WSL2 / ROS2 terminal 中：

```bash
cd <factory-floor-digital-twin>
source /opt/ros/humble/setup.bash
python3 ros2_publisher/machine_publisher.py
```

### 3. 啟動 ROS2-to-MQTT bridge

開另一個 WSL2 / ROS2 terminal：

```bash
cd <factory-floor-digital-twin>
source /opt/ros/humble/setup.bash
python3 bridge/ros2_to_mqtt.py
```

如果 bridge 連不上 broker，請檢查 `bridge/ros2_to_mqtt_config.py`：

```python
MQTT_BROKER_HOST = "10.255.255.254"
MQTT_BROKER_PORT = 1883
```

- bridge 與 broker 都在 Windows 本機時，通常可以用 `localhost`。
- bridge 在 WSL2、broker 在 Windows Docker 時，可能需要使用 Windows host 對 WSL2 可見的 IP。
- Omniverse extension 目前預設連 `localhost:1883`。

### 4. 啟動 Omniverse Kit app

在 Kit App Template repo 中：

```powershell
cd <your-workspace>\kit-app-template
.\repo.bat launch
```

選擇前面建立的 app，例如：

```text
guan_omniverse_practice.my_editor.kit
```

啟動後確認：

1. Extension Manager 中可找到並啟用 `Factory Floor Digital Twin` / `omni.factory.twin`。
2. 開啟 `USD_Explorer_Sample_NVD@10011\Usd_Explorer\Samples\Examples\2023_2\Factory\Factory.usd`，或其他已依 `config/machines.toml` 對齊 prim path 的 USD stage。
3. MQTT broker、publisher、bridge 都在執行。
4. Console 中出現 MQTT connect / subscribe / message log。

## Topic 與資料格式

ROS2 topic 格式：

```text
/factory/{machine_id}/{parameter}
```

MQTT topic 格式：

```text
factory/{machine_id}/{parameter}
```

範例 payload：

```json
{"machine_id": "m_00", "temperature": 72.5}
```

```json
{"machine_id": "m_00", "vibration": 3.2}
```

```json
{"machine_id": "m_00", "operation_mode": "RUNNING"}
```

支援的狀態與參數由 `config/thresholds.toml` 決定：

- `temperature`
- `vibration`
- `operation_mode`
- `RUNNING`
- `IDLE`
- `SHUTDOWN`
- `OFFLINE`

## 常見問題

### Extension 載入不到

請檢查：

- `kit-app-template/source/extensions/omni.factory.twin` 是否正確指向 `factory-floor-digital-twin/omniverse_extension`
- `.kit` 檔案是否有 `"omni.factory.twin" = {}`
- `.kit` 檔案的 extension search folder 是否包含 `${app}/../../../../source/extensions`
- 是否重新執行過 `.\repo.bat build`

### MQTT 沒有資料

請檢查：

- `docker compose up -d` 是否已啟動 broker
- `bridge/ros2_to_mqtt.py` 是否成功連線到 broker
- `ros2_publisher/machine_publisher.py` 是否持續發布資料
- WSL2 與 Windows/Docker 之間的 IP 是否正確

### USD prim 沒有變色

請檢查：

- 已開啟對應的 USD stage
- `config/machines.toml` 的 `usd_prim_path` 是否存在於目前 stage
- Omniverse Console 是否有 `Build collection fail, not found prim` 類似訊息

### Kit app 啟動很慢

Kit app 啟動時可能需要更新 extension cache，RTX shader 也可能需要數分鐘初始化。後續啟動通常會快很多。

## 開發備註

- `config/` 是 ROS2 publisher、bridge 與 Omniverse extension 的共同設定來源。
- 修改 `machines.toml` 後，需要確保 ROS2 topic、MQTT topic 與 USD prim path 都一致。
- 修改 `thresholds.toml` 可以調整警告/錯誤門檻、狀態顏色與透明度。
- `omniverse_extension/` 底下是 Omniverse extension 原始碼；開發時建議透過 Kit App Template 的 junction 載入，避免手動複製。
