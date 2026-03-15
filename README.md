# Stock Prediction Portal 🚀

A professional, full-stack stock market prediction application built with **React**, **Django REST Framework**, and **TensorFlow**. This portal provides real-time stock data analysis, moving averages, and future price predictions using a pre-trained LSTM (Long Short-Term Memory) model.

## ✨ Features
- **Accurate Predictions**: Uses a deep learning LSTM model to predict future price trends.
- **Unified Port Architecture**: Both frontend and backend serve on a single port (**3000**) via an Nginx reverse proxy.
- **Deep Analytics**: Real-time stock data fetching (via Yahoo Finance) with technical indicators like 100-day and 200-day moving averages.
- **Secure Authentication**: JWT-based login and registration system.
- **Rate Limiting**: Built-in protection against API abuse.
- **Dockerized Environment**: Fully containerized setup for consistent development and deployment.

## 🏗️ Architecture
The application is composed of four main services orchestrated by Docker Compose:
1. **Frontend**: React (Vite) application served by Nginx.
2. **Backend**: Django REST Framework API handling logic and ML predictions.
3. **Database**: PostgreSQL for persistent data storage.
4. **Cache**: Redis for high-performance caching and rate limiting.

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose installed on your system.

### Installation & Run
1. **Clone the repository**:
   ```bash
   git clone https://github.com/shikeb1/stock-prediction-modell.git
   cd stock-prediction-modell
   ```

2. **Setup Environment Variables**:
   Copy the example environment file and update it if necessary:
   ```bash
   cp .env.example .env
   ```

3. **Launch the Application**:
   ```bash
   docker-compose up --build -d
   ```

4. **Access the Portal**:
   - **Frontend UI**: [http://localhost:3000](http://localhost:3000)
   - **API Health Check**: [http://localhost:3000/api/v1/health/](http://localhost:3000/api/v1/health/)
   - **Django Admin**: [http://localhost:3000/admin/](http://localhost:3000/admin/)

## 🛠️ Development
You can use the provided `Makefile` for common tasks:
- `make build`: Rebuild images
- `make up`: Start services in background
- `make down`: Stop all services
- `make logs`: View logs
- `make migrate`: Apply database migrations

## 🛡️ Security
- All sensitive data is managed via environment variables.
- Production-ready Nginx configuration for secure routing.
- Throttling enabled on all public API endpoints.

## 📄 License
This project is for educational and research purposes.

---
**Happy Predicting! 🎯**
