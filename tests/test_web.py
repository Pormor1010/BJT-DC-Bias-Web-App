"""HTTP-level tests for the Flask routes."""

import unittest

from app import app


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_index_shows_form(self):
        res = self.client.get("/")

        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        for field in ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"):
            self.assertIn(f'name="{field}"', body)


class TestCalculate(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.valid = dict(
            vcc="12", r1="100", r2="22", rc="2.2", re="1", beta="100", vbe="0.70"
        )

    def test_post_returns_computed_values(self):
        res = self.client.post("/calculate", data=self.valid)

        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("8.052", body)  # VCE
        self.assertIn("1.230", body)  # IC in mA
        self.assertIn("1.942", body)  # VB


class TestInvalidInput(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.valid = dict(
            vcc="12", r1="100", r2="22", rc="2.2", re="1", beta="100", vbe="0.70"
        )

    def test_zero_vcc_shows_error(self):
        res = self.client.post("/calculate", data=dict(self.valid, vcc="0"))

        self.assertEqual(res.status_code, 200)
        self.assertIn("ข้อผิดพลาด", res.get_data(as_text=True))

    def test_non_numeric_shows_error(self):
        res = self.client.post("/calculate", data=dict(self.valid, vcc="abc"))

        self.assertEqual(res.status_code, 200)
        self.assertIn("ข้อผิดพลาด", res.get_data(as_text=True))

    def test_missing_field_shows_error(self):
        data = {k: v for k, v in self.valid.items() if k != "r1"}

        res = self.client.post("/calculate", data=data)

        self.assertEqual(res.status_code, 200)
        self.assertIn("ข้อผิดพลาด", res.get_data(as_text=True))


class TestDisplayAndLabels(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.valid = dict(
            vcc="12", r1="100", r2="22", rc="2.2", re="1", beta="100", vbe="0.70"
        )

    def test_form_labels_and_button_are_thai(self):
        body = self.client.get("/").get_data(as_text=True)
        for text in ("แรงดันไฟเลี้ยง", "ตัวต้านทานขา Base", "คำนวณ DC Bias"):
            self.assertIn(text, body)

    def test_region_is_shown_in_thai(self):
        res = self.client.post("/calculate", data=self.valid)
        self.assertIn("Active (ทำงานปกติ)", res.get_data(as_text=True))

    def test_warning_block_reaches_page(self):
        res = self.client.post("/calculate", data=dict(self.valid, rc="47"))
        body = res.get_data(as_text=True)
        self.assertIn("alert warning", body)
        self.assertIn("Saturation", body)

    def test_ib_displayed_in_microamps(self):
        res = self.client.post("/calculate", data=self.valid)
        self.assertIn("12.299", res.get_data(as_text=True))

    def test_vce_cell_has_value_and_unit(self):
        res = self.client.post("/calculate", data=self.valid)
        self.assertRegex(
            res.get_data(as_text=True), r"<th>VCE</th><td>8\.052 V</td>"
        )


if __name__ == "__main__":
    unittest.main()
