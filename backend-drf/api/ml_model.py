import os
import logging
import threading
import zipfile
import h5py
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Input
from django.conf import settings

logger = logging.getLogger(__name__)

_model_lock = threading.Lock()
_model = None
_model_load_error = None


def get_model():
    global _model, _model_load_error

    if _model is not None:
        return _model

    if _model_load_error is not None:
        raise RuntimeError(f"Model previously failed: {_model_load_error}")

    with _model_lock:
        if _model is not None:
            return _model

        model_path = os.path.join(
            settings.BASE_DIR, 'resources', 'stock_prediction_model.keras'
        )

        if not os.path.exists(model_path):
            _model_load_error = f"Not found: {model_path}"
            raise FileNotFoundError(_model_load_error)

        logger.info(f"Loading model from: {model_path}")

        try:
            # Step 1: Extract weights from the .keras zip archive
            weights_path = '/tmp/weights.h5'
            with zipfile.ZipFile(model_path, 'r') as z:
                with z.open('model.weights.h5') as src, open(weights_path, 'wb') as dst:
                    dst.write(src.read())
            logger.info("Weights extracted!")

            # Step 2: Rebuild the model architecture
            model = Sequential()
            model.add(Input(shape=(100, 1)))
            model.add(LSTM(units=128, activation='tanh', return_sequences=True))
            model.add(LSTM(units=64))
            model.add(Dense(25))
            model.add(Dense(1))
            model.compile(optimizer='adam', loss='mean_squared_error')

            # Step 3: Initialize model weights with a dummy prediction
            model.predict(np.zeros((1, 100, 1)), verbose=0)

            # Step 4: Manually load weights from the extracted h5 file
            with h5py.File(weights_path, 'r') as f:
                model.layers[0].set_weights([
                    f['layers/lstm/cell/vars/0'][:],
                    f['layers/lstm/cell/vars/1'][:],
                    f['layers/lstm/cell/vars/2'][:]
                ])
                model.layers[1].set_weights([
                    f['layers/lstm_1/cell/vars/0'][:],
                    f['layers/lstm_1/cell/vars/1'][:],
                    f['layers/lstm_1/cell/vars/2'][:]
                ])
                model.layers[2].set_weights([
                    f['layers/dense/vars/0'][:],
                    f['layers/dense/vars/1'][:]
                ])
                model.layers[3].set_weights([
                    f['layers/dense_1/vars/0'][:],
                    f['layers/dense_1/vars/1'][:]
                ])

            _model = model
            logger.info(f"✅ SUCCESS! Input: {_model.input_shape}")

        except Exception as e:
            _model_load_error = str(e)
            logger.error(f"❌ Failed: {e}")
            raise RuntimeError(f"Model load failed: {e}")

    return _model


def is_model_loaded():
    return _model is not None


def get_model_info():
    if _model is None:
        return {"loaded": False, "error": _model_load_error}
    return {
        "loaded": True,
        "input_shape": str(_model.input_shape),
        "output_shape": str(_model.output_shape),
        "total_params": _model.count_params(),
    }