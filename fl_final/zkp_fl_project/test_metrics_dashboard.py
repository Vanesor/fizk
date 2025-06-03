import unittest
import os
import json
import pandas as pd
from datetime import datetime, timezone

# Add project root to sys.path to allow direct import of enhanced_dashboard
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_dashboard import app, load_metrics_data, update_dashboard

# Define the path to a temporary metrics file for testing
TEST_METRICS_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fl_system', 'test_fl_metrics_log.json')
ORIGINAL_METRICS_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fl_system', 'fl_metrics_log.json')

class TestEnhancedDashboard(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        # Ensure the fl_system directory exists
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fl_system'), exist_ok=True)
        
        # Backup original metrics file if it exists
        if os.path.exists(ORIGINAL_METRICS_FILE_PATH):
            os.rename(ORIGINAL_METRICS_FILE_PATH, ORIGINAL_METRICS_FILE_PATH + ".bak")
        
        # Use TEST_METRICS_FILE_PATH for the dashboard during tests
        # This requires modifying where enhanced_dashboard looks for the file,
        # or more simply, creating the file at the location it expects (ORIGINAL_METRICS_FILE_PATH)
        self.dashboard_metrics_file = ORIGINAL_METRICS_FILE_PATH 

        self.sample_metrics_data = {
            "overall_start_time_iso": datetime.now(timezone.utc).timestamp() - 3600,
            "total_duration_sec_so_far": 3600,
            "rounds_history": [
                {
                    "round": 1, "auth_success": 2, "auth_fail": 0, "auth_time_sec": 0.5,
                    "proofs_aggregated": 2, "aggregation_valid": "✅", 
                    "proof_aggregation_time_sec": 1.2, "model_aggregation_time_sec": 0.8,
                    "agg_loss": 0.75, "agg_accuracy": 0.88, "round_duration_sec": 30.5
                },
                {
                    "round": 2, "auth_success": 1, "auth_fail": 1, "auth_time_sec": 0.6,
                    "proofs_aggregated": 1, "aggregation_valid": "✅", 
                    "proof_aggregation_time_sec": 0.9, "model_aggregation_time_sec": 0.7,
                    "agg_loss": 0.65, "agg_accuracy": 0.90, "round_duration_sec": 25.2
                },
                { # Round with missing data
                    "round": 3, "auth_success": 2, "auth_fail": 0, "auth_time_sec": None,
                    "proofs_aggregated": 2, "aggregation_valid": "N/A", 
                    "proof_aggregation_time_sec": 1.5, "model_aggregation_time_sec": None,
                    "agg_loss": None, "agg_accuracy": None, "round_duration_sec": 28.0
                }
            ]
        }
        with open(self.dashboard_metrics_file, 'w') as f:
            json.dump(self.sample_metrics_data, f, indent=4)

    def tearDown(self):
        """Tear down after test methods."""
        if os.path.exists(self.dashboard_metrics_file):
            os.remove(self.dashboard_metrics_file)
        
        # Restore original metrics file
        if os.path.exists(ORIGINAL_METRICS_FILE_PATH + ".bak"):
            os.rename(ORIGINAL_METRICS_FILE_PATH + ".bak", ORIGINAL_METRICS_FILE_PATH)

    def test_01_load_metrics_data(self):
        """Test the load_metrics_data function."""
        print(f"🧪 Testing load_metrics_data from: {self.dashboard_metrics_file}")
        df, raw_data = load_metrics_data()
        
        self.assertIsNotNone(df, "DataFrame should not be None")
        self.assertIsNotNone(raw_data, "Raw data should not be None")
        self.assertEqual(len(df), len(self.sample_metrics_data["rounds_history"]), "DataFrame rows should match history length")
        self.assertIn("overall_start_time_iso", raw_data, "overall_start_time_iso should be in raw_data")
        self.assertTrue(pd.api.types.is_numeric_dtype(df['agg_loss']), "agg_loss should be numeric")
        self.assertTrue(pd.api.types.is_numeric_dtype(df['agg_accuracy']), "agg_accuracy should be numeric")
        self.assertTrue(pd.api.types.is_numeric_dtype(df['round_duration_sec']), "round_duration_sec should be numeric")

    def test_02_update_dashboard_callback(self):
        """Test the main update_dashboard callback function."""
        print("🧪 Testing update_dashboard callback")
        # The callback takes n_intervals as input, which is not used by our load_metrics_data
        summary_children, table_columns, table_data, loss_fig, accuracy_fig, timing_fig, auth_proof_fig = update_dashboard(0)

        self.assertTrue(len(summary_children) > 0, "Summary should have content")
        
        self.assertTrue(len(table_columns) > 0, "Table should have columns")
        self.assertEqual(len(table_data), len(self.sample_metrics_data["rounds_history"]), "Table data rows should match history length")
        
        self.assertIn('data', loss_fig, "Loss figure should have data key")
        self.assertIn('layout', loss_fig, "Loss figure should have layout key")
        # Check if actual plot data exists if source data was valid
        if not pd.Series(self.sample_metrics_data["rounds_history"][0]['agg_loss']).isna().all():
             self.assertTrue(len(loss_fig['data']) > 0, "Loss figure should contain plot data")


        self.assertIn('data', accuracy_fig, "Accuracy figure should have data key")
        if not pd.Series(self.sample_metrics_data["rounds_history"][0]['agg_accuracy']).isna().all():
            self.assertTrue(len(accuracy_fig['data']) > 0, "Accuracy figure should contain plot data")

        self.assertIn('data', timing_fig, "Timing figure should have data key")
        self.assertTrue(len(timing_fig['data']) > 0, "Timing figure should contain plot data")
        
        self.assertIn('data', auth_proof_fig, "Auth/Proof figure should have data key")
        self.assertTrue(len(auth_proof_fig['data']) > 0, "Auth/Proof figure should contain plot data")

    def test_03_load_metrics_data_file_not_found(self):
        """Test load_metrics_data when the file does not exist."""
        print("🧪 Testing load_metrics_data with no file")
        if os.path.exists(self.dashboard_metrics_file):
            os.remove(self.dashboard_metrics_file)
        
        df, raw_data = load_metrics_data()
        self.assertTrue(df.empty, "DataFrame should be empty if file not found")
        self.assertEqual(raw_data, {}, "Raw data should be empty dict if file not found")

    def test_04_load_metrics_data_empty_json(self):
        """Test load_metrics_data with an empty JSON file."""
        print("🧪 Testing load_metrics_data with empty JSON")
        with open(self.dashboard_metrics_file, 'w') as f:
            json.dump({}, f)
        df, raw_data = load_metrics_data()
        self.assertTrue(df.empty, "DataFrame should be empty for empty JSON")
        self.assertEqual(raw_data, {}, "Raw data should be the loaded empty dict") # or specific content if load_metrics_data initializes it

    def test_05_load_metrics_data_malformed_json(self):
        """Test load_metrics_data with a malformed JSON file."""
        print("🧪 Testing load_metrics_data with malformed JSON")
        with open(self.dashboard_metrics_file, 'w') as f:
            f.write("this is not json")
        df, raw_data = load_metrics_data()
        self.assertTrue(df.empty, "DataFrame should be empty for malformed JSON")
        self.assertEqual(raw_data, {}, "Raw data should be empty for malformed JSON")
        
    def test_06_dashboard_client_get(self):
        """Test if the dashboard page loads (basic client GET)."""
        print("🧪 Testing basic dashboard page GET")
        # app.test_client() is for Flask apps. Dash uses a similar concept.
        # For Dash, you typically run the server and use an HTTP client.
        # This is a simplified check that the app object is there.
        self.assertIsNotNone(app.server, "Dash app server should exist")
        # A more thorough test would involve running the app in a thread
        # and using requests to GET the page, then check status and content.
        # For now, we'll just check if the layout can be accessed.
        try:
            layout_str = str(app.layout) # Accessing the layout
            self.assertTrue(len(layout_str) > 0, "App layout should not be empty")
        except Exception as e:
            self.fail(f"Could not access app.layout: {e}")


if __name__ == '__main__':
    print("🧪 Running Enhanced ZKP FL Dashboard Tests")
    print("============================================================")
    # Ensure that the enhanced_dashboard.METRICS_FILE_PATH is set to our test file for the duration of the tests
    # This is a bit tricky as the dashboard script loads its path at import time.
    # The setUp method now writes to the *actual* file path the dashboard uses.
    
    # Store original METRICS_FILE_PATH from enhanced_dashboard
    original_dashboard_path_source = None
    if hasattr(sys.modules['enhanced_dashboard'], 'METRICS_FILE_PATH'):
        original_dashboard_path_source = sys.modules['enhanced_dashboard'].METRICS_FILE_PATH
        sys.modules['enhanced_dashboard'].METRICS_FILE_PATH = ORIGINAL_METRICS_FILE_PATH # Ensure it uses the one we manage

    unittest.main(verbosity=2)

    # Restore original path in module if changed
    if original_dashboard_path_source:
         sys.modules['enhanced_dashboard'].METRICS_FILE_PATH = original_dashboard_path_source