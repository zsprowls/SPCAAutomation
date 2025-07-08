# Deployment Guide

## Current Status ✅
Your app is already running and accessible at:
- **Local**: http://localhost:8050
- **Network**: http://192.168.1.152:8050 (accessible from other devices on your network)

## Deployment Options

### 1. **Simple Network Deployment** (Recommended for Internal Use)
Your app is already accessible to other devices on your network. Anyone on your local network can access it at `http://192.168.1.152:8050`.

**To start:**
```bash
python run_app.py
```

### 2. **Production Deployment with Gunicorn**
For more robust deployment with better performance and stability:

**Install production dependencies:**
```bash
pip install gunicorn
```

**Start production server:**
```bash
./deploy.sh production
```

**Or manually:**
```bash
gunicorn --config gunicorn_config.py wsgi:app.server
```

### 3. **System Service Deployment** (Advanced)
For automatic startup and background running:

**Create systemd service file:**
```bash
sudo nano /etc/systemd/system/pathways-viewer.service
```

**Add this content:**
```ini
[Unit]
Description=Pathways for Care Viewer
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/PathwaysUpdate
Environment=PATH=/path/to/your/python/bin
ExecStart=/path/to/your/python/bin/gunicorn --config gunicorn_config.py wsgi:app.server
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable pathways-viewer
sudo systemctl start pathways-viewer
```

## Access URLs

### Development
- **Local**: http://localhost:8050
- **Network**: http://192.168.1.152:8050

### Production
- **Local**: http://localhost:8050
- **Network**: http://your-server-ip:8050

## Configuration

### Port Configuration
To change the port, edit `gunicorn_config.py`:
```python
bind = "0.0.0.0:YOUR_PORT"
```

### Worker Configuration
Adjust workers based on your server capacity:
```python
workers = 2  # Increase for more CPU cores
```

## Security Considerations

### For Internal Network Use (Current Setup)
- ✅ Already secure for internal network access
- ✅ No external internet access required
- ✅ Firewall protection from external access

### For External Access (Not Recommended)
If you need external access, consider:
- Reverse proxy (nginx)
- SSL/TLS certificates
- Authentication system
- Firewall configuration

## Monitoring

### Check if app is running:
```bash
curl http://localhost:8050
```

### View logs:
```bash
# Development
python run_app.py

# Production
gunicorn --config gunicorn_config.py wsgi:app.server --log-level debug
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8050
lsof -i :8050

# Kill process
kill -9 PID
```

### Permission Issues
```bash
chmod +x deploy.sh
chmod +x run_app.py
```

### Cache Issues
```bash
# Rebuild cache
python build_cache.py
```

## Performance Tips

1. **Use production mode** for better performance
2. **Adjust workers** based on CPU cores
3. **Monitor memory usage** with large datasets
4. **Rebuild cache** if images are slow to load

## Next Steps

Your app is already successfully deployed and accessible! For most internal use cases, the current setup is perfect.

If you need:
- **External access**: Set up reverse proxy and SSL
- **Multiple users**: Consider load balancing
- **High availability**: Set up systemd service
- **Monitoring**: Add logging and health checks 