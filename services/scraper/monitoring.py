import json
import os
import time
from datetime import datetime
from typing import Dict, Any

EVALUATION_FILE = "services/scraper/scraper_evaluation.json"

class ScraperEvaluation:
    """Tracks scraping health and success metrics."""
    
    @staticmethod
    def _get_abs_path() -> str:
        """Helper to get absolute path to evaluation file."""
        # Use relative to project root
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), EVALUATION_FILE)

    @staticmethod
    def load_metrics() -> Dict[str, Any]:
        """Load metrics from the evaluation JSON file."""
        path = ScraperEvaluation._get_abs_path()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {"total_runs": 0, "spiders": {}}
        return {"total_runs": 0, "spiders": {}}

    @staticmethod
    def record_run(spider_name: str, count: int, success: bool, error: str = ""):
        """Record the outcome of a scraping run."""
        metrics = ScraperEvaluation.load_metrics()
        
        # Initialize spider if new
        if "spiders" not in metrics:
            metrics["spiders"] = {}
        
        if spider_name not in metrics["spiders"]:
            metrics["spiders"][spider_name] = {
                "success_count": 0,
                "fail_count": 0,
                "total_items_scraped": 0,
                "last_run": "",
                "last_error": ""
            }
            
        spider = metrics["spiders"][spider_name]
        
        if success:
            spider["success_count"] += 1
            spider["total_items_scraped"] += count
        else:
            spider["fail_count"] += 1
            spider["last_error"] = error
            
        spider["last_run"] = datetime.now().isoformat()
        metrics["total_runs"] = metrics.get("total_runs", 0) + 1
        
        # Save back to file
        path = ScraperEvaluation._get_abs_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(metrics, f, indent=2)

    @staticmethod
    def get_summary():
        """Get a human-readable summary of the metrics."""
        metrics = ScraperEvaluation.load_metrics()
        print("\n--- Scraper Evaluation Summary ---")
        print(f"Total Runs: {metrics.get('total_runs', 0)}")
        for name, data in metrics.get("spiders", {}).items():
            success_rate = (data['success_count'] / (data['success_count'] + data['fail_count'])) * 100 if (data['success_count'] + data['fail_count']) > 0 else 0
            print(f"Spider: {name}")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Items Scraped: {data['total_items_scraped']}")
            print(f"  Last Run: {data['last_run']}")
        print("-" * 34)
