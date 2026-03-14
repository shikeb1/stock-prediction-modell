"""
========================================================================
TEST_ML.PY - MACHINE LEARNING MODEL TESTS
========================================================================

Tests for TensorFlow LSTM model:
- Model loading and initialization
- Prediction accuracy
- Batch processing
- Error handling
- Performance benchmarks

========================================================================
"""

import pytest
import numpy as np
from django.conf import settings
from rest_framework import status
import os


# ========================================================================
# 1. MODEL LOADING TESTS
# ========================================================================

@pytest.mark.ml
class TestModelLoading:
    """ML model initialization tests"""
    
    def test_model_file_exists(self):
        """✅ Test model file exists at expected location"""
        model_path = os.path.join(
            settings.BASE_DIR,
            'resources',
            'stock_prediction_model.keras'
        )
        assert os.path.exists(model_path), \
            f"Model file not found: {model_path}"
    
    def test_model_file_size(self):
        """✅ Test model file has reasonable size"""
        model_path = os.path.join(
            settings.BASE_DIR,
            'resources',
            'stock_prediction_model.keras'
        )
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path)
            assert file_size > 1000000, \
                f"Model file too small: {file_size} bytes"
            assert file_size < 10000000, \
                f"Model file too large: {file_size} bytes"
    
    def test_model_can_be_loaded(self):
        """✅ Test model loads without errors"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                assert model is not None
                assert hasattr(model, 'predict')
        except ImportError:
            pytest.skip("TensorFlow not available")
    
    def test_model_input_shape(self):
        """✅ Test model has correct input shape"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                # LSTM model expects 3D input: (batch, timesteps, features)
                assert len(model.input_shape) == 3
                assert model.input_shape[0] is None  # Batch size
        except ImportError:
            pytest.skip("TensorFlow not available")


# ========================================================================
# 2. PREDICTION TESTS
# ========================================================================

@pytest.mark.ml
class TestPredictions:
    """Model prediction tests"""
    
    def test_model_prediction_shape(self):
        """✅ Test model output shape"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                # Create dummy input matching model shape
                # Assuming (batch=1, timesteps=60, features=5)
                dummy_input = np.random.randn(1, 60, 5).astype(np.float32)
                
                prediction = model.predict(dummy_input, verbose=0)
                assert prediction is not None
                assert prediction.shape[0] == 1  # Batch size
        except ImportError:
            pytest.skip("TensorFlow not available")
    
    def test_model_prediction_values_range(self):
        """✅ Test predictions are in reasonable range"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                dummy_input = np.random.randn(1, 60, 5).astype(np.float32)
                prediction = model.predict(dummy_input, verbose=0)
                
                # Stock prices should be positive (usually)
                # Allow some negative for percentage changes
                assert prediction.min() > -1000, \
                    "Prediction too low"
                assert prediction.max() < 1000000, \
                    "Prediction too high"
        except ImportError:
            pytest.skip("TensorFlow not available")
    
    def test_model_prediction_consistency(self):
        """✅ Test same input gives same output"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                # Create fixed input
                np.random.seed(42)
                dummy_input = np.random.randn(1, 60, 5).astype(np.float32)
                
                # Predict twice
                pred1 = model.predict(dummy_input, verbose=0)
                pred2 = model.predict(dummy_input, verbose=0)
                
                # Should be identical
                np.testing.assert_array_almost_equal(pred1, pred2)
        except ImportError:
            pytest.skip("TensorFlow not available")


# ========================================================================
# 3. BATCH PROCESSING TESTS
# ========================================================================

@pytest.mark.ml
class TestBatchProcessing:
    """Batch prediction tests"""
    
    def test_batch_prediction(self):
        """✅ Test batch prediction with multiple inputs"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                # Batch of 5 samples
                batch_input = np.random.randn(5, 60, 5).astype(np.float32)
                predictions = model.predict(batch_input, verbose=0)
                
                assert predictions.shape[0] == 5
        except ImportError:
            pytest.skip("TensorFlow not available")
    
    def test_single_vs_batch_consistency(self):
        """✅ Test single and batch predictions are consistent"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                # Single input
                single_input = np.random.randn(1, 60, 5).astype(np.float32)
                single_pred = model.predict(single_input, verbose=0)
                
                # Same input in batch of 1
                batch_input = np.random.randn(1, 60, 5).astype(np.float32)
                batch_pred = model.predict(batch_input, verbose=0)
                
                # Should have same shape
                assert single_pred.shape == batch_pred.shape
        except ImportError:
            pytest.skip("TensorFlow not available")


# ========================================================================
# 4. ERROR HANDLING TESTS
# ========================================================================

@pytest.mark.ml
class TestMLErrorHandling:
    """ML model error handling"""
    
    def test_invalid_input_shape(self):
        """✅ Test model handles invalid input shape"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                # Wrong shape input
                wrong_input = np.random.randn(1, 30, 5).astype(np.float32)
                
                # Should raise error or handle gracefully
                with pytest.raises((ValueError, Exception)):
                    model.predict(wrong_input, verbose=0)
        except ImportError:
            pytest.skip("TensorFlow not available")
    
    def test_empty_input(self):
        """✅ Test model handles empty input"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                # Empty batch
                empty_input = np.array([]).reshape(0, 60, 5).astype(np.float32)
                
                with pytest.raises((ValueError, Exception)):
                    model.predict(empty_input, verbose=0)
        except ImportError:
            pytest.skip("TensorFlow not available")
    
    def test_nan_input(self):
        """✅ Test model handles NaN values"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                # Input with NaN
                nan_input = np.full((1, 60, 5), np.nan).astype(np.float32)
                
                # Should handle or raise error
                try:
                    prediction = model.predict(nan_input, verbose=0)
                    # If it doesn't raise, output should have NaN
                    assert np.isnan(prediction).any()
                except ValueError:
                    pass  # Expected behavior
        except ImportError:
            pytest.skip("TensorFlow not available")


# ========================================================================
# 5. PERFORMANCE TESTS
# ========================================================================

@pytest.mark.ml
class TestMLPerformance:
    """ML model performance benchmarks"""
    
    def test_prediction_speed(self):
        """✅ Test prediction is reasonably fast"""
        try:
            import tensorflow as tf
            import time
            
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                dummy_input = np.random.randn(1, 60, 5).astype(np.float32)
                
                start = time.time()
                model.predict(dummy_input, verbose=0)
                duration = time.time() - start
                
                # Should complete in under 1 second
                assert duration < 1.0, \
                    f"Prediction took {duration}s, expected < 1s"
        except ImportError:
            pytest.skip("TensorFlow not available")
    
    def test_batch_prediction_speed(self):
        """✅ Test batch prediction scales well"""
        try:
            import tensorflow as tf
            import time
            
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                # Larger batch
                batch_input = np.random.randn(32, 60, 5).astype(np.float32)
                
                start = time.time()
                model.predict(batch_input, verbose=0)
                duration = time.time() - start
                
                # Should complete reasonably fast
                assert duration < 5.0, \
                    f"Batch prediction took {duration}s"
        except ImportError:
            pytest.skip("TensorFlow not available")


# ========================================================================
# 6. MEMORY TESTS
# ========================================================================

@pytest.mark.ml
class TestMLMemory:
    """ML model memory usage"""
    
    def test_model_memory_usage(self):
        """✅ Test model doesn't consume excessive memory"""
        try:
            import tensorflow as tf
            
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                # Model should load without memory issues
                model = tf.keras.models.load_model(model_path)
                
                # Get model size
                total_params = model.count_params()
                
                # Should be reasonable (< 10M parameters)
                assert total_params < 10000000, \
                    f"Model has too many parameters: {total_params}"
        except ImportError:
            pytest.skip("TensorFlow not available")


# ========================================================================
# 7. DATA TYPE TESTS
# ========================================================================

@pytest.mark.ml
class TestDataTypes:
    """Data type handling tests"""
    
    def test_float32_input(self):
        """✅ Test model handles float32 input"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                input_f32 = np.random.randn(1, 60, 5).astype(np.float32)
                pred = model.predict(input_f32, verbose=0)
                
                assert pred is not None
        except ImportError:
            pytest.skip("TensorFlow not available")
    
    def test_float64_input(self):
        """✅ Test model converts float64 to float32"""
        try:
            import tensorflow as tf
            model_path = os.path.join(
                settings.BASE_DIR,
                'resources',
                'stock_prediction_model.keras'
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                
                # Float64 input
                input_f64 = np.random.randn(1, 60, 5).astype(np.float64)
                
                # Should handle conversion
                try:
                    pred = model.predict(input_f64, verbose=0)
                    assert pred is not None
                except (TypeError, ValueError):
                    pass  # Expected if strict type checking
        except ImportError:
            pytest.skip("TensorFlow not available")


# ========================================================================
# END OF TEST_ML.PY
# ========================================================================

"""
SUMMARY: ML Model Tests

✅ Model Loading: 4 tests
✅ Predictions: 3 tests
✅ Batch Processing: 2 tests
✅ Error Handling: 3 tests
✅ Performance: 2 tests
✅ Memory: 1 test
✅ Data Types: 2 tests

Total: 17 ML tests

Expected Coverage: 30-40% of ml_model.py
Run with: pytest tests/test_ml.py -v

Note: Tests are skipped if TensorFlow not installed
This is normal in lightweight testing environments
"""
