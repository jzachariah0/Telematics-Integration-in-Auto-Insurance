"""
InsurityAI Test Suite
Basic unit tests for pipeline verification and import validation
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / 'src'))


class TestImports(unittest.TestCase):
    """Test that all critical modules can be imported successfully"""
    
    def test_feature_imports(self):
        """Test feature engineering module imports"""
        try:
            from features.build_features import build_features
            self.assertTrue(callable(build_features))
        except ImportError as e:
            self.fail(f"Failed to import build_features: {e}")
    
    def test_model_imports(self):
        """Test model training module imports"""
        try:
            from models.train import train_models
            self.assertTrue(callable(train_models))
        except ImportError as e:
            self.fail(f"Failed to import train_models: {e}")
    
    def test_pricing_imports(self):
        """Test pricing module imports"""
        try:
            from pricing.run_pricing import run_pricing_pipeline
            self.assertTrue(callable(run_pricing_pipeline))
        except ImportError as e:
            self.fail(f"Failed to import run_pricing_pipeline: {e}")
    
    def test_api_imports(self):
        """Test API server imports"""
        try:
            from api.server import app
            self.assertIsNotNone(app)
        except ImportError as e:
            self.fail(f"Failed to import FastAPI app: {e}")


class TestDataStructure(unittest.TestCase):
    """Test that required data files and directories exist"""
    
    def setUp(self):
        self.project_root = Path(__file__).parent.parent
    
    def test_required_directories_exist(self):
        """Test that all required directories exist"""
        required_dirs = [
            'data', 'data/raw', 'models', 'src', 'docs', 'bin'
        ]
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            self.assertTrue(full_path.exists(), f"Required directory missing: {dir_path}")
            self.assertTrue(full_path.is_dir(), f"Path exists but is not a directory: {dir_path}")
    
    def test_raw_data_exists(self):
        """Test that raw data files exist"""
        raw_data_files = [
            'data/raw/trips.parquet',
            'data/raw/trips_meta.parquet'
        ]
        for file_path in raw_data_files:
            full_path = self.project_root / file_path
            self.assertTrue(full_path.exists(), f"Raw data file missing: {file_path}")
    
    def test_config_files_exist(self):
        """Test that configuration files exist"""
        config_files = [
            'requirements.txt',
            '.env.example',
            'README.md',
            'Makefile'
        ]
        for file_path in config_files:
            full_path = self.project_root / file_path
            self.assertTrue(full_path.exists(), f"Config file missing: {file_path}")


class TestBuildScripts(unittest.TestCase):
    """Test that build scripts exist and are properly structured"""
    
    def setUp(self):
        self.project_root = Path(__file__).parent.parent
        self.bin_dir = self.project_root / 'bin'
    
    def test_build_scripts_exist(self):
        """Test that all build scripts exist"""
        scripts = ['setup.sh', 'train.sh', 'serve.sh']
        for script in scripts:
            script_path = self.bin_dir / script
            self.assertTrue(script_path.exists(), f"Build script missing: {script}")
    
    def test_scripts_are_executable(self):
        """Test that scripts have executable content"""
        scripts = ['setup.sh', 'train.sh', 'serve.sh']
        for script in scripts:
            script_path = self.bin_dir / script
            with open(script_path, 'r') as f:
                content = f.read()
                self.assertTrue(content.startswith('#!/bin/bash'), 
                              f"Script missing shebang: {script}")
                self.assertIn('set -e', content, 
                            f"Script missing error handling: {script}")


class TestModelArtifacts(unittest.TestCase):
    """Test model artifacts when they exist"""
    
    def setUp(self):
        self.project_root = Path(__file__).parent.parent
        self.models_dir = self.project_root / 'models'
    
    def test_models_directory_structure(self):
        """Test that models directory exists and is structured correctly"""
        self.assertTrue(self.models_dir.exists(), "Models directory missing")
        self.assertTrue(self.models_dir.is_dir(), "Models path is not a directory")
    
    def test_model_files_when_trained(self):
        """Test model files exist if training has been run"""
        model_files = ['glm.pkl', 'lgbm.pkl']
        
        # Only test if at least one model exists (training has been run)
        models_exist = any((self.models_dir / f).exists() for f in model_files)
        
        if models_exist:
            for model_file in model_files:
                model_path = self.models_dir / model_file
                self.assertTrue(model_path.exists(), 
                              f"Model file missing after training: {model_file}")


class TestPipelineIntegrity(unittest.TestCase):
    """Test pipeline configuration and parameter consistency"""
    
    def test_ewma_parameters(self):
        """Test EWMA parameters are within valid ranges"""
        try:
            from pricing.run_pricing import EWMA_LAMBDA, MONTHLY_CAP_PCT, QUARTERLY_CAP_PCT
            
            # EWMA lambda should be between 0 and 1
            self.assertGreaterEqual(EWMA_LAMBDA, 0.0, "EWMA lambda must be >= 0")
            self.assertLessEqual(EWMA_LAMBDA, 1.0, "EWMA lambda must be <= 1")
            
            # Rate caps should be positive and reasonable
            self.assertGreater(MONTHLY_CAP_PCT, 0.0, "Monthly cap must be positive")
            self.assertLess(MONTHLY_CAP_PCT, 1.0, "Monthly cap should be < 100%")
            
            self.assertGreater(QUARTERLY_CAP_PCT, 0.0, "Quarterly cap must be positive")
            self.assertLess(QUARTERLY_CAP_PCT, 1.0, "Quarterly cap should be < 100%")
            
            # Quarterly cap should be larger than monthly
            self.assertGreater(QUARTERLY_CAP_PCT, MONTHLY_CAP_PCT, 
                             "Quarterly cap should be larger than monthly cap")
            
        except ImportError:
            self.skipTest("Pricing module not available for parameter testing")


class TestDocumentation(unittest.TestCase):
    """Test that required documentation files exist"""
    
    def setUp(self):
        self.project_root = Path(__file__).parent.parent
        self.docs_dir = self.project_root / 'docs'
    
    def test_documentation_files_exist(self):
        """Test that all required documentation files exist"""
        required_docs = [
            'data_dictionary.md',
            'design_choices.md',
            'dpia.md',
            'filing_brief.md',
            'kpis.md',
            'model_card.md'
        ]
        
        for doc_file in required_docs:
            doc_path = self.docs_dir / doc_file
            self.assertTrue(doc_path.exists(), f"Documentation file missing: {doc_file}")
    
    def test_metrics_directory_exists(self):
        """Test that metrics directory with visualizations exists"""
        metrics_dir = self.docs_dir / 'metrics'
        self.assertTrue(metrics_dir.exists(), "Metrics directory missing")
        
        # Check for some key metric files
        metric_files = ['calibration_plot.png', 'lift_chart.png', 'shap_global.png']
        for metric_file in metric_files:
            metric_path = metrics_dir / metric_file
            self.assertTrue(metric_path.exists(), f"Metric file missing: {metric_file}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)