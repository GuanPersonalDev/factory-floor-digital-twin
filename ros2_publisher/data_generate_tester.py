from data_generate_implement import NewtonCoolingTrend, EMANoise, PoissonAnomaly
from data_generate_base import SensorSimulator
import matplotlib.pyplot as plt

temperature_sensor = SensorSimulator(
    trend= NewtonCoolingTrend(idle=25.0, target=65.0, tau=30.0),
    noise= EMANoise(alpha=1.0, sigma=0.3, initial= 25.0),
    anomaly= PoissonAnomaly(trigger_prob=0.02, delta_warning=10.0, delta_error=25.0, duration=30, baseline_target=65.0)
)

vibration_sensor = SensorSimulator(
    trend= NewtonCoolingTrend(idle= 2.0, target=2.0, tau=1.0),
    noise = EMANoise(alpha=0.15, sigma=0.3, initial= 2.0),
    anomaly= PoissonAnomaly(trigger_prob= 0.02, delta_warning=3.5, delta_error=9.0, duration=30, baseline_target= 2.0)
)


counter = 0
all_data = []
TEMPERATURE_KEY = "temperature"
VIBRATION_KEY = "vibration"
while counter < 300:
    counter += 1
    temp = temperature_sensor.next_value()
    vib = vibration_sensor.next_value()
    data = {TEMPERATURE_KEY: temp, VIBRATION_KEY: vib}
    all_data.append(data)

steps = range(len(all_data))
temps = [d[TEMPERATURE_KEY] for d in all_data]
vibrations = [d[VIBRATION_KEY] for d in all_data]

fig, (ax_temp, ax_vib) = plt.subplots(2, 1, figsize=(12, 6), sharex= True)
fig.suptitle('Sensor Data', fontsize=14)

ax_temp.plot(steps, temps, color='tomato', linewidth=1.2)
ax_temp.set_ylabel('Temperature (°C)')
ax_temp.grid(True, alpha=0.3)

ax_vib.plot(steps, vibrations, color='steelblue', linewidth=1.2)
ax_vib.set_ylabel('Vibration')
ax_vib.set_xlabel('Step')
ax_vib.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
