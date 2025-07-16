
# Google Cloud SQL Setup Instructions

## 1. Create Google Cloud SQL Instance

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Navigate to SQL > Instances
3. Click "Create Instance"
4. Choose MySQL 8.0
5. Configure:
   - Instance ID: pathways-care-db
   - Password: (create a strong password)
   - Region: Choose closest to you
   - Machine type: db-f1-micro (free tier) or db-n1-standard-1
   - Storage: 10GB minimum

## 2. Create Database and User

1. Go to your SQL instance
2. Click "Databases" tab
3. Create database: `pathways_care`
4. Click "Users" tab
5. Create user: `pathways_user` with password
6. Grant privileges: SELECT, INSERT, UPDATE, DELETE, CREATE, DROP

## 3. Configure Network Access

1. Go to "Connections" tab
2. Add your IP address to "Authorized networks"
3. Or use "Public IP" for development (not recommended for production)

## 4. Download SSL Certificates (Optional but Recommended)

1. Go to "Connections" tab
2. Download SSL certificates:
   - Server CA certificate
   - Client certificate
   - Client private key

## 5. Update Configuration

1. Edit `cloud_config.json`
2. Update with your actual instance details
3. Set secure passwords

## 6. Run Migration

```bash
python cloud_migration_setup.py --migrate
```

## 7. Test Connection

```bash
python cloud_migration_setup.py --test
```
