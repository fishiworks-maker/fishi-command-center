import unittest
from src.fishi.export import transform


class ExportTests(unittest.TestCase):
    def test_crosspost_and_snapshot(self):
        rows, metrics = transform([{"id":"abc", "created_utc":0, "subreddit":"test", "crosspost_parent":"t3_xyz", "score":7, "num_comments":2}], "FISHI_WORKS", "2026-10-13T00:00:00+00:00")
        self.assertEqual(rows[0]["publication_type"], "crosspost")
        self.assertEqual(rows[0]["source_post_id"], "t3_xyz")
        self.assertEqual(metrics[0]["metric_period"], "cumulative_at_capture")
        self.assertEqual(metrics[0]["captured_utc"], "2026-10-13T00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
