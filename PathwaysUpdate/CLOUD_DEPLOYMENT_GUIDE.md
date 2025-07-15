# Pathways for Care - Cloud Deployment Guide

This guide will help you migrate from local SQLite to Google Cloud SQL MySQL and deploy your application for remote access.

## 🚀 Quick Start

1. **Setup Cloud Infrastructure** (15 minutes)
2. **Migrate Data** (5-10 minutes)
3. **Deploy Application** (5 minutes)
4. **Test Remote Access** (2 minutes)

## 📋 Prerequisites

- Google Cloud account (free tier available)
- Python 3.8+ installed
- Basic familiarity with command line

## 🏗️ Step 1: Setup Cloud Infrastructure

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable billing (required for Cloud SQL)

### 1.2 Create Cloud SQL Instance

1. Navigate to **SQL > Instances**
2. Click **"Create Instance"**
3. Choose **MySQL 8.0**
4. Configure settings:
   ```
   Instance ID: pathways-care-db
   Password: [Create strong password]
   Region: us-central1 (or closest to you)
   Machine type: db-f1-micro (free tier)
   Storage: 10GB
   ```
5. Click **"Create Instance"**

### 1.3 Create Database and User

1. Go to your SQL instance
2. Click **"Databases"** tab
3. Click **"Create Database"**
   - Database name: `pathways_care`
4. Click **"Users"** tab
5. Click **"Add User Account"**
   - Username: `pathways_user`
   - Password: [Create password]
   - Host: `%` (allows all IPs)

### 1.4 Configure Network Access

1. Go to **"Connections"** tab
2. Under **"Networking"**:
   - Add your IP address to **"Authorized networks"**
   - Or use **"Public IP"** for development (not recommended for production)

### 1.5 Download SSL Certificates (Optional but Recommended)

1. In **"Connections"** tab
2. Download:
   - Server CA certificate
   - Client certificate
   - Client private key
3. Save them in your project directory

## 🔧 Step 2: Setup Local Environment

### 2.1 Install Dependencies

```bash
cd PathwaysUpdate
pip install -r requirements_cloud.txt
```

### 2.2 Generate Configuration Files

```bash
python cloud_migration_setup.py --setup
```

This creates:
- `cloud_config.json` - Database configuration
- `mysql_schema.sql` - Database schema
- `CLOUD_SETUP_INSTRUCTIONS.md` - This guide

### 2.3 Update Configuration

Edit `cloud_config.json` with your actual values:

```json
{
  "cloud_sql": {
    "instance_name": "your-project:us-central1:pathways-care-db",
    "database_name": "pathways_care",
    "user": "pathways_user",
    "password": "your-actual-password",
    "host": "34.123.45.67",  // Your instance IP
    "port": 3306,
    "ssl_ca": "server-ca.pem",
    "ssl_cert": "client-cert.pem",
    "ssl_key": "client-key.pem"
  }
}
```

## 📊 Step 3: Migrate Data

### 3.1 Test Connection

```bash
python cloud_migration_setup.py --check
```

### 3.2 Run Migration

```bash
python migrate_to_cloud.py
```

This will:
- Create backup of your SQLite database
- Create MySQL tables
- Migrate all data
- Validate the migration

### 3.3 Verify Migration

Check that all data was transferred correctly:
- Record counts match
- Data integrity maintained
- All tables created

## 🌐 Step 4: Deploy Application

### 4.1 Local Testing with Cloud Database

```bash
streamlit run streamlit_cloud_app.py
```

In the sidebar, check **"Use Cloud Database (MySQL)"** to test cloud connectivity.

### 4.2 Deploy to Streamlit Cloud (Recommended)

1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/pathways-care.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file: `streamlit_cloud_app.py`
   - Deploy

3. **Configure Environment Variables**
   In Streamlit Cloud settings, add:
   ```
   GOOGLE_CLOUD_SQL_HOST=your-instance-ip
   GOOGLE_CLOUD_SQL_USER=pathways_user
   GOOGLE_CLOUD_SQL_PASSWORD=your-password
   GOOGLE_CLOUD_SQL_DATABASE=pathways_care
   ```

### 4.3 Alternative: Deploy to Google Cloud Run

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements_cloud.txt .
   RUN pip install -r requirements_cloud.txt
   
   COPY . .
   EXPOSE 8080
   
   CMD ["streamlit", "run", "streamlit_cloud_app.py", "--server.port=8080", "--server.address=0.0.0.0"]
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud builds submit --tag gcr.io/your-project/pathways-care
   gcloud run deploy pathways-care --image gcr.io/your-project/pathways-care --platform managed
   ```

## 🔒 Step 5: Security & Production Setup

### 5.1 Database Security

1. **Use Private IP** (recommended for production)
2. **Enable SSL connections**
3. **Restrict network access**
4. **Use strong passwords**
5. **Enable automated backups**

### 5.2 Application Security

1. **Environment variables** for sensitive data
2. **HTTPS only**
3. **Authentication** (consider adding login)
4. **Rate limiting**

### 5.3 Monitoring

1. **Cloud SQL monitoring**
2. **Application logs**
3. **Performance metrics**

## 🧪 Step 6: Testing

### 6.1 Test Local Cloud Connection

```bash
python test_cloud_connection.py
```

### 6.2 Test Remote Access

1. Open your deployed application
2. Verify data loads correctly
3. Test editing functionality
4. Check image loading
5. Test export functionality

### 6.3 Performance Testing

- Load time with large datasets
- Concurrent user access
- Database query performance

## 🔄 Step 7: Maintenance

### 7.1 Regular Backups

Google Cloud SQL provides automated backups, but you can also:
- Export data regularly
- Keep local SQLite as backup
- Test restore procedures

### 7.2 Updates

- Keep dependencies updated
- Monitor for security patches
- Test updates in staging environment

### 7.3 Monitoring

- Set up alerts for database issues
- Monitor application performance
- Track usage patterns

## 🆘 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check IP whitelist
   - Verify credentials
   - Test SSL certificates

2. **Migration Errors**
   - Check data types
   - Verify schema compatibility
   - Review error logs

3. **Performance Issues**
   - Optimize queries
   - Add indexes
   - Consider caching

### Getting Help

- Check Google Cloud SQL documentation
- Review Streamlit deployment guides
- Check application logs

## 💰 Cost Estimation

### Google Cloud SQL (Free Tier)
- **db-f1-micro**: Free (limited to 1GB RAM)
- **Storage**: $0.17/GB/month
- **Network**: $0.12/GB

### Estimated Monthly Cost
- **Development**: $0-5/month
- **Production**: $20-50/month (depending on usage)

## 🎉 Success!

Once deployed, you'll have:
- ✅ Remote access to your database
- ✅ Real-time updates from anywhere
- ✅ Scalable infrastructure
- ✅ Automated backups
- ✅ Professional monitoring

Your Pathways for Care application is now cloud-ready and accessible from anywhere in the world! 