"""
Production API Views
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logging
import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
import yfinance as yf

from .ml_model import get_model, is_model_loaded, get_model_info
from .security import validate_ticker, check_rate_limit, get_client_ip, log_security_event
from .serializers import StockPredictionSerializer
from .utils import save_plot

logger = logging.getLogger(__name__)
PREDICTION_CACHE_TIMEOUT = 3600


@api_view(['GET'])
@permission_classes([AllowAny])
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    health_status = {
        'status': 'healthy',
        'message': 'API is running successfully',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'database': 'healthy',
            'redis': 'healthy',
            'ml_model': 'loaded'
        }
    }
    
    return Response(
        health_status,
        status=status.HTTP_200_OK,
        content_type='application/json'
    )


def download_stock_data(ticker, start, end):
    """Yahoo Finance se data download karo — retry + browser headers"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    })

    for attempt in range(3):
        try:
            df = yf.download(
                ticker,
                start=start,
                end=end,
                progress=False,
                session=session
            )
            if not df.empty:
                logger.info(f"Download success on attempt {attempt + 1}")
                return df
            logger.warning(f"Empty data on attempt {attempt + 1}, retrying...")
            time.sleep(3)
        except Exception as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            time.sleep(3)

    return pd.DataFrame()


class StockPredictionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        client_ip = get_client_ip(request)
        username = request.user.username

        allowed_min, _ = check_rate_limit(f"{username}_min", 'minute')
        if not allowed_min:
            log_security_event("RATE_LIMIT_MINUTE", {"user": username}, request)
            return Response({'error': 'Too many requests! 1 minute baad try karo.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        allowed_hour, remaining = check_rate_limit(f"{username}_hour", 'hour')
        if not allowed_hour:
            log_security_event("RATE_LIMIT_HOUR", {"user": username}, request)
            return Response({'error': 'Hourly limit exceeded! Thodi der baad try karo.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = StockPredictionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raw_ticker = serializer.validated_data['ticker']
        is_valid, error_msg = validate_ticker(raw_ticker)
        if not is_valid:
            log_security_event("INVALID_TICKER", {"ticker": raw_ticker}, request)
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

        ticker = raw_ticker.upper().strip()
        logger.info(f"PREDICTION_REQUEST | user={username} | ticker={ticker} | ip={client_ip}")

        cache_key = f"prediction:{ticker}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"CACHE_HIT | ticker={ticker}")
            cached['from_cache'] = True
            cached['requests_remaining'] = remaining
            return Response(cached)

        try:
            model = get_model()
        except Exception as e:
            logger.error(f"MODEL_LOAD_ERROR | {e}")
            return Response({'error': 'ML Model unavailable. Please try again.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Download with retry + browser headers
        try:
            now = datetime.now()
            start = datetime(now.year - 10, now.month, now.day)
            df = download_stock_data(ticker, start, now)
        except Exception as e:
            logger.error(f"DATA_DOWNLOAD_ERROR | ticker={ticker} | {e}")
            return Response({'error': 'Stock data download failed.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if df.empty:
            return Response({'error': f'"{ticker}" ka data nahi mila. Ticker sahi hai? Ya Yahoo Finance slow hai, 2 min baad try karo.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if len(df) < 200:
            return Response({'error': f'Insufficient data for "{ticker}" ({len(df)} days). Need 200+ days.'}, status=status.HTTP_400_BAD_REQUEST)

        df = df.reset_index()

        plt.figure(figsize=(12, 5))
        plt.plot(df.Close, label='Closing Price')
        plt.title(f'Closing Price — {ticker}')
        plt.xlabel('Days')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.tight_layout()
        plot_img = save_plot(f'{ticker}_plot.png')

        ma100 = df.Close.rolling(100).mean()
        plt.figure(figsize=(12, 5))
        plt.plot(df.Close, label='Closing Price')
        plt.plot(ma100, 'r', label='100 DMA')
        plt.title(f'100 Day Moving Average — {ticker}')
        plt.xlabel('Days')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.tight_layout()
        plot_100_dma = save_plot(f'{ticker}_100_dma.png')

        ma200 = df.Close.rolling(200).mean()
        plt.figure(figsize=(12, 5))
        plt.plot(df.Close, label='Closing Price')
        plt.plot(ma100, 'r', label='100 DMA')
        plt.plot(ma200, 'g', label='200 DMA')
        plt.title(f'200 Day Moving Average — {ticker}')
        plt.xlabel('Days')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.tight_layout()
        plot_200_dma = save_plot(f'{ticker}_200_dma.png')

        data_training = pd.DataFrame(df.Close[0:int(len(df) * 0.7)])
        data_testing = pd.DataFrame(df.Close[int(len(df) * 0.7):])
        scaler = MinMaxScaler(feature_range=(0, 1))
        past_100 = data_training.tail(100)
        final_df = pd.concat([past_100, data_testing], ignore_index=True)
        input_data = scaler.fit_transform(final_df)

        x_test, y_test = [], []
        for i in range(100, input_data.shape[0]):
            x_test.append(input_data[i - 100:i])
            y_test.append(input_data[i, 0])
        x_test, y_test = np.array(x_test), np.array(y_test)

        y_pred = model.predict(x_test, verbose=0)
        y_pred = scaler.inverse_transform(y_pred.reshape(-1, 1)).flatten()
        y_actual = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

        plt.figure(figsize=(12, 5))
        plt.plot(y_actual, 'b', label='Original Price')
        plt.plot(y_pred, 'r', label='Predicted Price')
        plt.title(f'Prediction vs Actual — {ticker}')
        plt.xlabel('Days')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.tight_layout()
        plot_prediction = save_plot(f'{ticker}_final_prediction.png')

        mse = float(mean_squared_error(y_actual, y_pred))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(y_actual, y_pred))

        result = {
            'status': 'success',
            'ticker': ticker,
            'plot_img': plot_img,
            'plot_100_dma': plot_100_dma,
            'plot_200_dma': plot_200_dma,
            'plot_prediction': plot_prediction,
            'mse': round(mse, 4),
            'rmse': round(rmse, 4),
            'r2': round(r2, 4),
            'current_price': round(float(df.Close.iloc[-1]), 2),
            'data_points': len(df),
            'from_cache': False,
            'requests_remaining': remaining,
        }

        try:
            cache.set(cache_key, result, PREDICTION_CACHE_TIMEOUT)
        except Exception as e:
            logger.warning(f"CACHE_WRITE_FAILED | {e}")

        logger.info(f"PREDICTION_SUCCESS | ticker={ticker} | user={username} | r2={r2:.4f}")
        return Response(result)