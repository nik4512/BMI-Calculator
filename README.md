# BMI Analytics Pro (BMI Calculator with Matplotlib Charts)

A modern, comprehensive Body Mass Index (BMI) calculator and health analytics application built with **Python**, **Tkinter**, and **Matplotlib**.

---

## ✨ Features

- **Accurate WHO Standard Classification**:
  - Underweight ($< 18.5$)
  - Normal Weight ($18.5 - 24.9$)
  - Overweight ($25.0 - 29.9$)
  - Obesity Class I ($30.0 - 34.9$)
  - Obesity Class II ($35.0 - 39.9$)
  - Obesity Class III ($\ge 40.0$)

- **Dual Unit Systems**:
  - **Metric**: Weight in kg, Height in cm
  - **Imperial**: Weight in lbs, Height in feet & inches
  - Instant automatic conversion between units without losing data.

- **Personalized Health Insights**:
  - Calculates your optimal healthy weight range for your exact height.
  - Indicates the exact weight difference (gain/lose) needed to reach the healthy range.
  - Estimated **Basal Metabolic Rate (BMR)** calculation (Mifflin-St Jeor equation) factoring in age and biological sex.
  - Actionable lifestyle, nutritional, and risk evaluation advice.

- **Interactive Matplotlib Visualizations**:
  - 📊 **BMI Spectrum Gauge**: Color-coded WHO range segments with a dynamic pointer indicating your exact position on the spectrum.
  - ⚖️ **Weight vs Target Zone**: Bar comparison of current weight against minimum and maximum healthy weights, with target zone shading.
  - 📈 **Historical Progress Trend**: Line chart tracking your weight and BMI over time with a shaded healthy target zone ($18.5 - 24.9$).

- **Historical Log & Data Persistence**:
  - Saves your measurements automatically or manually into `bmi_history.json`.
  - Built-in data table with delete, clear, and single-click CSV export.
  - Includes a "Load Sample History" button to immediately preview multi-month trend charts.

- **Modern UI & Themes**:
  - Sleek Dark Mode and Light Mode with seamless theme toggling.
  - Clean card-based layout and responsive design.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ (Python 3.14+ supported)
- Tkinter (standard with Python on Windows)
- Matplotlib

### Installation

1. Navigate to the project directory:
   ```bash
   cd "C:\Users\SMRITI SHARMA\.gemini\antigravity\scratch\bmi-calculator"
   ```

2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

### Running the Application

Launch the calculator with:
```bash
python bmi_calculator.py
```

---

## 📁 Project Structure

```
bmi-calculator/
├── bmi_calculator.py    # Main GUI application with Tkinter & Matplotlib
├── requirements.txt     # Python package requirements
├── bmi_history.json     # Saved user measurement logs (auto-created)
└── README.md            # Documentation and instructions
```
