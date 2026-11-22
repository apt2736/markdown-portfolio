---
layout: default
title: "Project Overview: TriageBox Smart ML-Integrated Triage Device"
---

# Project Overview: TriageBox Smart ML-Integrated Triage Device

<div class="tag-list">
  <span class="tag">PIMNAS 39 Silver &amp; Bronze</span>
  <span class="tag">STM32</span>
  <span class="tag">ESP32-S3</span>
  <span class="tag">LoRa</span>
  <span class="tag">LightGBM</span>
</div>

<br />

<div align="center">
  <img alt="TriageBox PIMNAS 39 Double Award" src="../../assets/images/pimnas_39_double_award.jpeg" width="460" loading="lazy" decoding="async" />
  <br />
  <sub>TriageBox team at Pekan Ilmiah Mahasiswa Nasional (PIMNAS) 39, awarded Silver Medal (2nd Place) in Presentation and Bronze Medal (3rd Place) in Poster under the PKM-Karsa Cipta (PKM-KC1) division.</sub>
</div>

## 1. Disaster Context, Problem Statement & Team Profile

**TriageBox** (*Alat Triase Cerdas Terintegrasi Machine Learning untuk Mempercepat Triase Korban Massal Bencana Gempa*) was developed under **Program Kreativitas Mahasiswa - Karsa Cipta (PKM-KC) 2026** at **Institut Teknologi Sepuluh Nopember (ITS)** to address two bottlenecks in mass-casualty earthquake response: slow manual vital-sign acquisition and unmonitored clinical deterioration at field evacuation posts.

During major earthquakes in Indonesia, field medical teams face overwhelming casualty surges alongside damaged hospital and telecommunications infrastructure:
- **High Casualty-to-Responder Ratios & Infrastructure Loss**: In the August 2026 M 7.7 Nagekeo (NTT / Flores) earthquake, BNPB and Ministry of Health reports recorded 135 fatalities, 1,787 injured casualties (385 requiring intensive care), and over 185,000 displaced residents across 444 evacuation points, while 19 of 190 community health centers (*puskesmas*) ceased operation, 3 of 21 hospitals suffered heavy structural damage, 200 of 812 cellular towers went offline, and each healthcare worker had to cover an average of 314 evacuees.
- **Unmonitored Post-Earthquake Deterioration**: Over 64% of the fatalities (87 of 135 deaths) occurred indirectly after the initial tremor, including evacuees whose condition deteriorated unmonitored while waiting at field posts prior to referral.
- **Slow Paper-Based Triage (5–10 Minutes per Patient)**: In both the 2022 Cianjur earthquake (~2,300 injured casualties) and recent disaster deployments, field responders still rely on manual paper triage tags (*lembar triase*). Measuring four core vital signs (blood pressure, heart rate, oxygen saturation, and respiratory rate) across four separate instruments and filling out paper forms takes **5 to 10 minutes per casualty**.

**TriageBox** replaces four separate diagnostic tools and paper tags with a single portable wearable node that acquires four vital signs in **57 seconds**, classifies triage urgency on-device in **~3 seconds** (**≤ 1 minute total**), tags the patient via an **RFID wristband**, and transmits live vital telemetry over an independent **500+ meter LoRa radio network** to a command post dashboard without needing grid electricity or cellular coverage.

### PKM-KC ITS 2026 Team & Roles

| Member | Department | Role & Primary Responsibilities |
| :--- | :--- | :--- |
| **Dr. Rudy Dikairono, S.T., M.T.** | Electrical Engineering | **Faculty Advisor** |
| **Yuke Brilliant Hestiavin** | Computer Engineering | **Team Leader & System Integrator**: System architecture, firmware-to-dashboard integration, and full-stack IoT command dashboard development. |
| **Aslam Pandu Tasminto** | Mathematics | **Software & Machine Learning Engineer**: Clinical START/ESI triage protocol mapping, physiological dataset preprocessing, and design, training, and evaluation of the on-device LightGBM cuffless blood pressure regression and triage classification models. |
| **Andika Rizky Noval Nugraha** | Electrical Engineering | **Electrical & Embedded Hardware Engineer**: Schematic and custom PCB design, sensor conditioning circuits (AD8232 ECG, MAX30102 PPG, RFID, LoRa), and STM32 signal acquisition firmware. |
| **Izza Azizah** | Biomedical Engineering | **Mechanical & Biomedical Engineer**: Portable enclosure CAD design, clinical sensor accuracy benchmarking against medical reference instruments, and user research with emergency medical personnel. |
| **Clarissa Aydin Rahmazea** | Information Technology | **Branding & Publication Lead**: Public relations (`@triagebox.its`), visual communication, scientific poster design, and documentation. |

---

## 2. System Architecture & Hardware Specifications

TriageBox is split into three parts: reusable **Wearable Patient Nodes** strapped to casualties during triage and waiting-room monitoring, a pole-mounted **LoRa Receiver Station** at the medical tent, and a local **Command Center Dashboard** for medical coordinators.

<div align="center">
  <table>
    <tr>
      <th align="center">Wearable Patient Node</th>
      <th align="center">LoRa Receiver Station</th>
      <th align="center">Command Center Dashboard</th>
    </tr>
    <tr>
      <td align="center">
        <img src="../../assets/images/triagebox_node.png" alt="TriageBox Wearable Patient Node" style="max-height: 250px; width: auto;" loading="lazy" decoding="async" />
      </td>
      <td align="center">
        <img src="../../assets/images/triagebox_station.png" alt="TriageBox LoRa Receiver Station" style="max-height: 250px; width: auto;" loading="lazy" decoding="async" />
      </td>
      <td align="center">
        <img src="../../assets/images/triagebox_dashboard.png" alt="TriageBox Command Center Web Dashboard" style="max-height: 250px; width: auto;" loading="lazy" decoding="async" />
      </td>
    </tr>
    <tr>
      <td align="center"><em>4-vital-sign acquisition, RFID scanner, and on-device LightGBM inference</em></td>
      <td align="center"><em>Multi-node 433 MHz LoRa receiver with W5500 Ethernet bridge</em></td>
      <td align="center"><em>Real-time casualty triage board, Red-alert notifications, and RFID history</em></td>
    </tr>
  </table>
</div>

### Subsystem Technical Specifications

| Tier | Component / Parameter | Specification |
| :--- | :--- | :--- |
| **Wearable Patient Node** | **Dual Microcontrollers** | **STM32F411CEU6** (real-time sensor acquisition & digital bandpass filtering) + **ESP32-S3** (on-device LightGBM inference, touch UI, and radio control) |
| | **Physiological Sensors** | **MAX30102** finger clip (dual-wavelength PPG for SpO2 & pulse transit waveform), **AD8232** limb clamp (Lead-I ECG for heart rate & R-peak timing), oxygen-mask microphone via **GX12-5** aviation jack (respiratory rate, with manual UI fallback in noisy field zones) |
| | **Patient Identification** | Integrated **RFID Scanner** paired with per-casualty RFID wristbands |
| | **User Interface & Alerts** | 4-inch touchscreen display, 4 physical navigation buttons, high-visibility triage **LED indicator** (Red / Yellow / Green), and audible buzzer |
| | **Wireless & Power** | **SX1278 433 MHz LoRa** transceiver with external whip antenna; **3.7 V 5,000 mAh LiPo** battery (**7.5 hours** continuous runtime) |
| | **Dimensions & Weight** | **8.7 cm × 5.25 cm × 18.2 cm**; **471 grams** |
| **LoRa Receiver Station** | **Controller & Networking** | **ESP32** + **SX1278 433 MHz LoRa** module + **W5500 Ethernet** module in a weather-resistant pole-mounted enclosure; receives packets from multiple field nodes and publishes to the local server via **MQTT** |
| **Command Center Dashboard** | **Software Stack** | **Nest.js** backend, **React.js** frontend, **MQTT** message broker, and **PostgreSQL** database; provides real-time triage distribution, unacknowledged **Red (Critical)** alerts, per-wristband vital history, and hospital referral readiness |

### End-to-End System Dataflow (*Alur Sistem*)

```mermaid
flowchart LR
    subgraph Input ["1. Node Sensor & UI Input"]
        PPG["MAX30102 Finger Sensor<br/>(SpO2 & PPG Waveform)"]
        ECG["AD8232 Clamp Sensor<br/>(Heart Rate & ECG Waveform)"]
        MIC["Mask Microphone / UI<br/>(Respiratory Rate)"]
        UI_IN["Touchscreen Manual Input<br/>(Age, Sex, Airway, RFID Tag)"]
    end

    subgraph Processing ["2. On-Device Edge Processing"]
        MCU["STM32F411CEU6 + ESP32-S3"]
        FILT["Digital Sensor Filtering<br/>(Bandpass & R-Peak Detection)"]
        ML_BP["LightGBM Blood Pressure<br/>Regression (SBP & DBP)"]
        ML_TRI["LightGBM Triage Classifier<br/>(ESI 1-4 to START Mapping)"]
    end

    subgraph Output ["3. On-Node Triage Output"]
        LCD["4-Inch Touchscreen<br/>& Triage LED Indicator"]
        RED["Red (Resuscitation / ESI 1)"]
        YEL["Yellow (Urgent / ESI 2)"]
        GRN["Green (Stable / ESI 3-4)"]
    end

    subgraph IoT ["4. Field Post IoT & Dashboard"]
        LORA["LoRa 433 MHz Link -> Station<br/>-> W5500 Ethernet -> MQTT"]
        DB["PostgreSQL Database"]
        DASH["TriageBox Dashboard<br/>(Nest.js & React.js)<br/>Category Alerts & Patient Table"]
    end

    PPG --> FILT
    ECG --> FILT
    MIC --> FILT
    UI_IN --> ML_TRI
    MCU --- FILT
    FILT --> ML_BP
    ML_BP --> ML_TRI

    ML_TRI --> LCD
    ML_TRI --> RED
    ML_TRI --> YEL
    ML_TRI --> GRN

    ML_TRI --> LORA
    LORA --> DB
    DB --> DASH

    classDef redNode fill:#e63946,stroke:#9b2226,stroke-width:2px,color:#ffffff;
    classDef yelNode fill:#f4a261,stroke:#ca6702,stroke-width:2px,color:#0f172a;
    classDef grnNode fill:#2a9d8f,stroke:#1d7066,stroke-width:2px,color:#ffffff;

    class RED redNode;
    class YEL yelNode;
    class GRN grnNode;
```

### 5-Step Field Triage Workflow

1. **Casualty Arrival**: The injured survivor arrives at the field triage post and receives an RFID identification wristband.
2. **Sensor Attachment**: The responder attaches the MAX30102 finger clip, AD8232 ECG limb clamps, and respiratory mask sensor.
3. **Node Acquisition & Edge Inference**: The TriageBox node is strapped to the patient's arm, scans the RFID wristband, records 57 seconds of synchronized waveforms, and computes blood pressure and START triage priority on-device in ~3 seconds.
4. **LoRa Telemetry Transmission**: Vital signs and the assigned triage category (Red, Yellow, or Green) are displayed immediately on the node's 4-inch screen and LED, while telemetry packets are broadcast over 433 MHz LoRa to the post's Receiver Station.
5. **Post Monitoring & Referral**: The Command Center Dashboard logs the patient's record, highlights critical Red casualties or sudden category downgrades, and tracks waiting patients until hospital evacuation.

---

## 3. Core Machine Learning Pipeline

My primary technical contribution to TriageBox was designing, training, and optimizing the two-stage on-device **LightGBM** pipeline that enables cuffless blood pressure estimation from ECG/PPG pulse transit dynamics and maps clinical Emergency Severity Index (ESI) acuity predictions into 3-color START disaster triage priorities on the ESP32-S3 microcontroller:

<div class="card card-interactive">
  <div class="card-header">
    <div class="card-title"><a href="{{ '/pages/projects/ml_pipeline_triagebox.html' | relative_url }}">Machine Learning Pipeline based on LightGBM for Triage Classification and Blood Pressure Regression</a></div>
    <span class="card-date">Jul – Oct 2026</span>
  </div>
  <p>Two-stage LightGBM pipeline running on ESP32-S3: cuffless systolic and diastolic blood pressure estimation from ECG/PPG features (1.56 / 1.15 mmHg MAE), followed by ESI-to-START triage classification (94.24% Red sensitivity, 90.17% balanced accuracy).</p>
</div>

---

## 4. Verification Results & Technology Benchmarking

### Hardware & Software Verification Summary

| Subsystem | Verification Benchmark | Measured Result |
| :--- | :--- | :--- |
| **Heart Rate (AD8232 ECG)** | 5 post-exercise subjects × 5 trials vs. Easy ECG clinical monitor | **1.04 bpm MAE** |
| **Oxygen Saturation (MAX30102)** | 5 post-exercise subjects × 5 trials vs. commercial pulse oximeter | **0.8 percentage-point MAE** |
| **Cuffless Blood Pressure (LightGBM)** | 148 subjects, 444 recordings (Li et al., 2026); 70/20/10 train/val/test split | **1.56 mmHg SBP MAE / 1.15 mmHg DBP MAE** (2.51 s inference time) |
| **Triage Classification (LightGBM)** | 87,234 ESI encounters (Imanov & Dulger, 2026); 70/15/15 split mapped to START (Phattharapornjaroen et al., 2026) | **94.24% Red sensitivity / 90.17% 3-class balanced accuracy** (21.04 ms inference time) |
| **LoRa SX1278 Radio Link** | Field range & latency test across building-obstructed urban path with stock antenna | **504.75 m range** at **581 ms latency** |
| **Node Battery Endurance** | Continuous acquisition, screen, inference, and LoRa transmission on 5,000 mAh LiPo | **7.5 hours** runtime |

### Comparison with Existing Triage & Vital-Monitoring Technologies

| Parameter | RescueWave | Athena WVSM | E-Triage Tag | Biobeat | **TriageBox (Ours)** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Primary Function** | Digital triage tag | Vital sign monitor | Electronic triage tag | Blood pressure monitor | **Automated triage + continuous monitoring** |
| **Measured Vital Signs** | 0 | 4 | 2 | 5 | **4 (HR, SpO2, cuffless BP, RR)** |
| **Manual Clinical Inputs** | Color only | Triage color only | None | None | **3 fields (Age, Sex, Airway) + optional RR** |
| **Time to Triage Result** | Manual | Manual | ≥ 1 min | ≥ 5 min | **≤ 1 min (57 s capture + ~3 s inference)** |
| **Classification Compute** | Manual | Manual | Central Server | Cloud | **On-Device Edge ML (ESP32-S3)** |
| **Communication Link** | 7 km radio | 183 m wireless | Wi-Fi dependent | Internet dependent | **Self-contained LoRa (504.75 m NLOS)** |
| **Patient Identification** | QR code | None | None | None | **RFID Wristband** |
