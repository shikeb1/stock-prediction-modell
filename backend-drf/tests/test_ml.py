"""
ML Model Tests — test_ml.py
Machine Learning model ke tests.
Model sahi se load ho raha hai ya nahi check karte hain.
"""
import pytest
import numpy as np


class TestMLModelLoading:
    """ML Model loading ke tests — database ki zarurat nahi"""

    def test_ml_model_module_imports(self):
        """
        ml_model module import ho sakta hai ya nahi.
        Agar import fail ho toh baaki tests bhi fail honge.
        """
        try:
            from api.ml_model import get_model, is_model_loaded, get_model_info
            assert True
        except ImportError as e:
            pytest.fail(f"ml_model import failed: {e}")

    def test_model_info_function_exists(self):
        """
        get_model_info() function exist karta hai ya nahi.
        """
        from api.ml_model import get_model_info
        info = get_model_info()
        assert isinstance(info, dict)
        assert "loaded" in info

    def test_is_model_loaded_returns_bool(self):
        """
        is_model_loaded() boolean return karta hai.
        """
        from api.ml_model import is_model_loaded
        result = is_model_loaded()
        assert isinstance(result, bool)


class TestMLModelPrediction:
    """Model prediction ke tests — model load hone ke baad"""

    def test_model_input_shape(self):
        """
        Model ka input shape (None, 100, 1) hona chahiye.
        Matlab 100 dino ka data leke prediction deta hai.
        """
        from api.ml_model import is_model_loaded, get_model
        if not is_model_loaded():
            pytest.skip("Model file not available in test environment")

        model = get_model()
        assert model.input_shape == (None, 100, 1), \
            f"Expected (None, 100, 1), got {model.input_shape}"

    def test_model_output_shape(self):
        """
        Model ek single value predict karta hai (price).
        Output shape (None, 1) hona chahiye.
        """
        from api.ml_model import is_model_loaded, get_model
        if not is_model_loaded():
            pytest.skip("Model file not available in test environment")

        model = get_model()
        assert model.output_shape == (None, 1), \
            f"Expected (None, 1), got {model.output_shape}"

    def test_model_prediction_runs(self):
        """
        Model actual prediction de sakta hai ya nahi.
        Fake data bhejo — crash nahi hona chahiye.
        """
        from api.ml_model import is_model_loaded, get_model
        if not is_model_loaded():
            pytest.skip("Model file not available in test environment")

        model = get_model()
        fake_data = np.zeros((1, 100, 1))
        prediction = model.predict(fake_data, verbose=0)

        assert prediction is not None
        assert prediction.shape == (1, 1)
        assert not np.isnan(prediction).any(), "Prediction should not be NaN"


class TestSecurityValidation:
    """Security validation ke tests"""

    def test_validate_ticker_function_exists(self):
        """validate_ticker function exist karta hai"""
        from api.security import validate_ticker
        assert callable(validate_ticker)

    def test_valid_ticker_passes(self):
        """Valid ticker accept hota hai"""
        from api.security import validate_ticker
        is_valid, error = validate_ticker("AAPL")
        assert is_valid is True
        assert error is None or error == ""

    def test_empty_ticker_rejected(self):
        """Empty ticker reject hota hai"""
        from api.security import validate_ticker
        is_valid, error = validate_ticker("")
        assert is_valid is False

    def test_too_long_ticker_rejected(self):
        """Bahut lamba ticker reject hota hai"""
        from api.security import validate_ticker
        is_valid, error = validate_ticker("TOOLONGTICKER")
        assert is_valid is False

    def test_sql_injection_rejected(self):
        """SQL injection attempt reject hota hai"""
        from api.security import validate_ticker
        is_valid, error = validate_ticker("'; DROP TABLE--")
        assert is_valid is False

    def test_script_injection_rejected(self):
        """Script injection attempt reject hota hai"""
        from api.security import validate_ticker
        is_valid, error = validate_ticker("<script>alert(1)</script>")
        assert is_valid is False
