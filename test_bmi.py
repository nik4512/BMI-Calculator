"""
Unit tests for BMI calculation and classifications
"""

import unittest
from bmi_calculator import classify_bmi, BMI_CATEGORIES


class TestBMICalculations(unittest.TestCase):
    def test_classify_underweight(self):
        cat = classify_bmi(17.5)
        self.assertEqual(cat["name"], "Underweight")

    def test_classify_normal(self):
        cat = classify_bmi(22.0)
        self.assertEqual(cat["name"], "Normal Weight")

    def test_classify_overweight(self):
        cat = classify_bmi(27.5)
        self.assertEqual(cat["name"], "Overweight")

    def test_classify_obese_1(self):
        cat = classify_bmi(32.0)
        self.assertEqual(cat["name"], "Obesity Class I")

    def test_classify_obese_2(self):
        cat = classify_bmi(37.0)
        self.assertEqual(cat["name"], "Obesity Class II")

    def test_classify_obese_3(self):
        cat = classify_bmi(45.0)
        self.assertEqual(cat["name"], "Obesity Class III")

    def test_metric_formula(self):
        # 70 kg, 1.75 m
        weight_kg = 70.0
        height_m = 1.75
        bmi = weight_kg / (height_m ** 2)
        self.assertAlmostEqual(bmi, 22.857, places=2)

    def test_imperial_formula(self):
        # 154 lbs, 5 ft 9 in = 69 in
        weight_lbs = 154.0
        height_in = 69.0
        bmi = 703 * (weight_lbs / (height_in ** 2))
        self.assertAlmostEqual(bmi, 22.74, places=1)

    def test_healthy_range(self):
        height_m = 1.75
        min_wt = 18.5 * (height_m ** 2)
        max_wt = 24.9 * (height_m ** 2)
        self.assertAlmostEqual(min_wt, 56.65, places=1)
        self.assertAlmostEqual(max_wt, 76.25, places=1)


if __name__ == "__main__":
    unittest.main()
