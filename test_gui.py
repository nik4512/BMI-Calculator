"""
Headless / automated validation of BMICalculatorApp lifecycle and charts
"""

import tkinter as tk
from unittest.mock import patch
from bmi_calculator import BMICalculatorApp


def test_app_lifecycle():
    root = tk.Tk()
    root.withdraw()  # Don't show window on screen during automated test

    with patch("tkinter.messagebox.showinfo") as mock_info:
        app = BMICalculatorApp(root)

        # 1. Verify initial calculation
        assert app.current_result is not None, "Initial result should not be None"
        assert "bmi" in app.current_result, "Result should contain BMI"
        print(f"Default BMI: {app.current_result['bmi']:.2f} ({app.current_result['category']})")

        # 2. Test chart switching
        for tab in ("gauge", "weights", "trend"):
            app.switch_chart_tab(tab)
            assert app.active_chart_tab == tab

        # 3. Test unit switching
        app.unit_system.set("imperial")
        app._on_unit_change()
        print(f"Imperial BMI: {app.current_result['bmi']:.2f} ({app.current_result['category']})")

        # 4. Test theme toggle
        app.toggle_theme()
        assert app.current_theme == "light"
        app.toggle_theme()
        assert app.current_theme == "dark"

        # 5. Test sample data loading
        app.load_sample_history()
        assert len(app.history_records) == 6
        app.switch_chart_tab("trend")

        root.destroy()
        print("All GUI and chart tests passed successfully without any warnings or dialog hangs!")


if __name__ == "__main__":
    test_app_lifecycle()
