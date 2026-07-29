"""YAML config loading and validation tests"""
import pytest, os, yaml

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
MIN_YAML = {"analytics":1,"certification":2,"competitive":1,"marketplace":1,"pricing":3,"scoring":6}

def test_all_config_categories_exist():
    for cat in ["analytics","certification","competitive","marketplace","pricing","scoring"]:
        assert os.path.isdir(os.path.join(CONFIG_DIR, cat)), f"Missing: {cat}"

def test_yaml_files_per_category():
    for cat, expected in MIN_YAML.items():
        d = os.path.join(CONFIG_DIR, cat)
        if os.path.isdir(d):
            y = [f for f in os.listdir(d) if f.endswith(".yaml")]
            assert len(y) >= expected, f"{cat}: expected {expected}, got {len(y)}"

def test_all_yaml_parseable():
    for root, dirs, files in os.walk(CONFIG_DIR):
        for f in files:
            if f.endswith(".yaml"):
                with open(os.path.join(root, f), "r", encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
                    assert data is not None, f"{f} parsed to None"

def test_scoring_configs_have_weights():
    scoring_dir = os.path.join(CONFIG_DIR, "scoring")
    skip_weights = ["assessment.yaml"]
    for f in os.listdir(scoring_dir):
        if f.endswith(".yaml"):
            with open(os.path.join(scoring_dir, f), "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
            assert "schema_version" in data, f"{f} missing schema_version"
            if f not in skip_weights:
                assert "weights" in data, f"{f} missing weights"
