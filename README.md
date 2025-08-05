# Hybrid VPN API Backend

API backend untuk aplikasi SecureVPN yang menguruskan Hybrid VPN Approach dengan server loading dan configuration.

## 🚀 Deployment

### Railway Deployment
1. Connect repository ke Railway
2. Railway akan automatik detect Python project
3. Environment variables akan diset secara automatik
4. Health check endpoint: `/api/v1/health`

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Atau gunakan gunicorn untuk production-like environment
gunicorn wsgi:application --bind 0.0.0.0:5000
```

## 📊 API Endpoints

### Health Check
- `GET /api/v1/health` - Check API status

### Hybrid VPN API
- `GET /api/v1/servers` - Get server list untuk Hybrid VPN
- `GET /api/v1/locations` - Get location list
- `GET /api/v1/config` - Get VPN configuration (WireGuard)

### Analytics
- `POST /api/v1/track` - Track VPN connection
- `GET /api/v1/stats` - Get analytics statistics

## 🔧 Environment Variables

- `PORT` - Port untuk server (Railway set secara automatik)
- `FLASK_ENV` - Environment (development/production)

## 🛠️ Troubleshooting

### Common Issues:
1. **Port binding error** - Pastikan menggunakan `$PORT` environment variable
2. **Import error** - Pastikan semua dependencies dalam `requirements.txt`
3. **Health check failed** - Pastikan endpoint `/api/v1/health` berfungsi

### Railway Specific:
- Railway automatik set `PORT` environment variable
- Gunakan `gunicorn` untuk production deployment
- Health check timeout: 100 seconds
- Builder: Dockerfile (lebih reliable)

## 🧪 Testing

Test API endpoints:
```bash
# Health check
curl https://your-railway-url/api/v1/health

# Get servers
curl https://your-railway-url/api/v1/servers

# Get locations
curl https://your-railway-url/api/v1/locations

# Get VPN config
curl https://your-railway-url/api/v1/config?server_id=japan-tokyo-1
``` 