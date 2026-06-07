# Factory Floor Digital Twin Architecture

這份文件補充 README 中被精簡掉的架構與模組細節。README 保留 Demo、啟動流程與必要設定；本文件則用來說明資料流、各模組責任、設定檔與常見排查方向。

## 資料流

```text
ROS2 Machine Publisher
  -> /factory/{machine_id}/{parameter}
  -> ROS2 to MQTT Bridge
  -> factory/{machine_id}/{parameter}
  -> Mosquitto MQTT Broker
  -> Omniverse Kit Extension
  -> USD scene material / HUD / alert list / minimap / labels
```

流程說明：

1. `ros2_publisher/machine_publisher.py` 依照 `config/` 內的機台與門檻設定，每秒產生模擬資料。
2. Publisher 將資料發布到 ROS2 topic，例如 `/factory/m_00/temperature`。
3. `bridge/ros2_to_mqtt.py` 訂閱 ROS2 topic，將 JSON payload 轉送到 MQTT topic，例如 `factory/m_00/temperature`。
4. Mosquitto broker 透過 `docker-compose.yml` 啟動，預設監聽 `1883`。
5. Omniverse extension 訂閱 `factory/#`，收到資料後更新 machine model、狀態顏色與 UI。

## 專案目錄責任

```text
factory-floor-digital-twin/
├─ bridge/                 # ROS2 -> MQTT bridge
├─ config/                 # 共用設定與 topic resolver
├─ docs/                   # 架構與補充文件
├─ mosquitto/              # Mosquitto broker 設定
├─ omniverse_extension/    # Omniverse Kit Python extension
├─ ros2_publisher/         # ROS2 模擬資料產生器
└─ docker-compose.yml      # MQTT broker compose file
```

## `config/`

`config/` 是 ROS2 publisher、bridge 與 Omniverse extension 共用的設定來源。

- `machines.toml`：定義每台機器的 `machine_id`、顯示名稱、USD prim path 與 zone。
- `thresholds.toml`：定義參數列表、門檻值、狀態顏色與透明度。
- `topic_resolver.py`：統一產生 ROS2 topic、MQTT topic 與 MQTT subscribe pattern。
- `config_loader.py`：讀取 TOML，提供 `FactoryConfig` 與 `MachineConfig` 給其他模組使用。

### Topic 命名

ROS2 topic：

```text
/factory/{machine_id}/{parameter}
```

MQTT topic：

```text
factory/{machine_id}/{parameter}
```

MQTT subscribe pattern：

```text
factory/#
```

### 主要參數

目前主要支援：

- `temperature`
- `vibration`
- `operation_mode`

`operation_mode` 的常見值：

- `RUNNING`
- `IDLE`
- `SHUTDOWN`
- `OFFLINE`

## `ros2_publisher/`

`ros2_publisher/` 用來產生 Demo 用的模擬機台資料。

- `machine_publisher.py`：ROS2 node 入口。建立每台機器、每個參數的 publisher，並定期發布 JSON 字串。
- `topic_data_generator.py`：管理單台機器的狀態，依照 script phase 或預設行為產生當前資料。
- `data_generate_base.py`：感測資料模擬器的基本抽象。
- `data_generate_implement.py`：實作趨勢、雜訊與異常資料產生邏輯。
- `data_generate_tester.py`：資料產生邏輯的測試 / 觀察用程式。

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

## `bridge/`

`bridge/` 負責把 ROS2 topic 轉成 MQTT topic。

- `ros2_to_mqtt.py`：主要 bridge node。啟動後會讀取 `FactoryConfig`，為所有 machine / parameter 建立 ROS2 subscription，收到資料後 publish 到對應 MQTT topic。
- `ros2_to_mqtt_config.py`：MQTT broker host 與 port。

如果 bridge 在 WSL2 裡執行，而 Mosquitto broker 在 Windows Docker 裡執行，`MQTT_BROKER_HOST` 可能不能直接使用 `localhost`，需要依自己的 Windows / WSL2 網路設定調整。

## `omniverse_extension/`

`omniverse_extension/` 是 Omniverse Kit Python extension，會被接到既有 Kit App Template app 中執行。

### Extension metadata

- `omniverse_extension/config/extension.toml`
  - package title：`Factory Floor Digital Twin`
  - Python module：`omniverse_factory_twin`
  - dependencies：`omni.kit.uiapp`、`omni.ui.scene`、`omni.kit.viewport.registry`

### Core

- `omniverse_factory_twin/extension.py`
  - extension 入口。
  - 初始化 `FactoryConfig`、log、machine model、HUD、小地圖、label view 與 `PrimRenderManager`。
  - 訂閱 stage event，在 stage 開啟後建立需要的 UI 與 USD collection。
  - 收到 MQTT 訊息後，更新 log / model / material / UI。

- `omniverse_factory_twin/base_extension.py`
  - 封裝 Omniverse extension lifecycle。
  - 在 `on_startup` 建立 MQTT client，並註冊 Kit update event polling。
  - 在 `on_shutdown` 斷開 MQTT，清理 external module cache，避免設定修改後重啟 extension 仍使用舊 module。

- `omniverse_factory_twin/mqtt_client.py`
  - 使用 `paho-mqtt` 連線 broker。
  - 訂閱 topic 後將訊息放入 queue。
  - 由 Kit update loop 呼叫 `poll()` 取出訊息，避免直接在 MQTT callback 中更新 Omniverse UI / USD。

- `omniverse_factory_twin/factory_log.py`
  - 保存近期 MQTT 資料。
  - 提供 machine model 查詢最新模式與最新參數值。

- `omniverse_factory_twin/factory_events.py`
  - 專案事件 / 常數集中處。

- `omniverse_factory_twin/prim_render_manager.py`
  - 建立狀態 material。
  - 依照 `machines.toml` 的 USD prim path 建立 collection。
  - 根據 machine model 的 current color，將 material 套用到對應 collection。

### Model

- `model/machine_model.py`
  - 保存單台機器當前狀態。
  - 根據 log 計算 operation mode、severity、顏色與 dirty flag。

- `model/all_machine.py`
  - 管理所有 machine model。
  - 提供 overview、machine list、alert list、minimap 所需的 delegate data。

- `model/factory_map.py`
  - 計算工廠 layout / minimap 顯示資料。

- `model/machine_prim_solver.py`
  - 處理 machine 與 USD prim 對應。

### View

- `view/hud_panel_widget.py`
  - 組合主要 HUD panel。
  - 顯示 overview、machine info list 與 alert machines view。

- `view/factory_overview.py`、`view/factory_overview_delegate.py`
  - 顯示整體機台數量與狀態摘要。

- `view/machine_info_list.py`、`view/machine_info_list_delegate.py`
  - 顯示各機台目前參數與狀態。

- `view/alert_machines_view.py`、`view/alert_machines_view_delegate.py`
  - 顯示 warning / error 機台。

- `view/factory_mini_map_view.py`、`view/factory_mini_map_delegate.py`
  - 顯示 factory minimap。

- `view/machine_label_view.py`
  - 在 viewport / scene 上建立機台 label。

- `view/style_sheet.py`
  - 集中管理 UI 樣式。

## 狀態與顏色邏輯

`FactoryConfig.compute_severity()` 會根據 `thresholds.toml` 判斷參數 severity：

- value >= `error`：`ERROR`
- value >= `warning`：`WARNING`
- 其他：`NORMAL`

`FactoryConfig.resolve_color()` 會依據 operation mode 與 severity 回傳 RGBA：

- 一般狀態使用 `severity_color`。
- `SHUTDOWN` / `OFFLINE` 可透過 `operation_mode.override_color` 覆蓋顏色。
- 不同 operation mode 可透過 `operation_mode.opacity` 設定透明度。

`MachineModel` 在顏色改變時會標記 dirty flag，extension update loop 只更新 dirty machines 的 USD material。

## USD 場景假設

Demo 使用 NVIDIA 官方的 USD Explorer Sample Assets Pack：

```text
USD_Explorer_Sample_NVD@10011\Usd_Explorer\Samples\Examples\2023_2\Factory\Factory.usd
```

`config/machines.toml` 中的 `usd_prim_path` 對應這個 factory sample scene。若使用自己的 USD 場景，需要更新：

- `machine_id`
- `display_name`
- `usd_prim_path`
- `zone`

如果 Console 出現類似 `Build collection fail, not found prim`，通常代表 `usd_prim_path` 與目前開啟的 stage 不一致。

## 常見排查

### Extension 載入不到

檢查項目：

- `kit-app-template/source/extensions/omni.factory.twin` 是否正確指向 `factory-floor-digital-twin/omniverse_extension`。
- `.kit` 是否加入 `"omni.factory.twin" = {}`。
- `.kit` 的 extension search path 是否包含 Kit App Template 的 `source/extensions`。
- 若 app 是手動建立，`premake5.lua` 與 `repo.toml` 是否包含該 app。

### MQTT 沒有資料

檢查項目：

- `docker compose up -d` 是否已啟動 broker。
- `ros2_publisher/machine_publisher.py` 是否正在發布資料。
- `bridge/ros2_to_mqtt.py` 是否成功連到 broker。
- WSL2 與 Windows / Docker 之間的 broker host 是否正確。

### USD prim 沒有變色

檢查項目：

- 目前開啟的 stage 是否為 NVIDIA factory sample。
- `config/machines.toml` 的 `usd_prim_path` 是否存在於目前 stage。
- Console 是否有 collection / prim path 相關錯誤。

### Kit app 啟動較慢

Kit app 啟動時可能正在更新 extension cache 或初始化 RTX shader。首次或清 cache 後啟動會比較慢，後續通常會改善。
