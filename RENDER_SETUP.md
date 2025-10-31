# 🚀 Deploying File Converter to Render

This guide will help you deploy your file converter application to Render for daily use.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com) (free tier available)
2. **AWS Account**: For S3 file storage (Render doesn't persist uploaded files)
3. **GitHub Account**: Your code should be in a GitHub repository

## 🎯 Step-by-Step Deployment

### Step 1: Set Up AWS S3 (Required for File Storage)

Since Render's free tier doesn't persist files across deploys, you need S3 for file storage:

1. **Create an S3 Bucket**:
   - Go to AWS Console → S3
   - Click "Create bucket"
   - Name it (e.g., `file-converter-storage`)
   - Choose a region (e.g., `us-east-1`)
   - Uncheck "Block all public access" (we'll use IAM for security)
   - Click "Create bucket"

2. **Configure CORS for your bucket**:
   - Go to your bucket → Permissions → CORS
   - Add this configuration:
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
       "AllowedOrigins": ["*"],
       "ExposeHeaders": ["ETag"]
     }
   ]
   ```

3. **Create IAM User for Programmatic Access**:
   - Go to IAM → Users → Add user
   - Username: `file-converter-app`
   - Access type: Programmatic access
   - Attach policy: `AmazonS3FullAccess` (or create a custom policy for just your bucket)
   - Save the **Access Key ID** and **Secret Access Key** (you'll need these)

### Step 2: Push Your Code to GitHub

```bash
# If not already a git repository
git init
git add .
git commit -m "Prepare for Render deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/file-converter.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Render (Option A - Using render.yaml)

This is the easiest method - Render will automatically detect and configure everything:

1. **Go to Render Dashboard**:
   - Visit [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Blueprint"

2. **Connect Your Repository**:
   - Select your GitHub repository
   - Render will detect `render.yaml` and show you all services

3. **Add Environment Variables**:
   Before deploying, you need to add AWS credentials manually:
   
   - For **file-converter-web** service:
     - `AWS_ACCESS_KEY_ID`: Your AWS Access Key
     - `AWS_SECRET_ACCESS_KEY`: Your AWS Secret Key
     - `AWS_STORAGE_BUCKET_NAME`: Your S3 bucket name
     - `AWS_S3_REGION_NAME`: Your S3 region (e.g., `us-east-1`)
   
   - For **file-converter-worker** service:
     - Same AWS credentials as above

4. **Deploy**:
   - Click "Apply"
   - Render will create all services: PostgreSQL, Redis, Web, and Worker
   - Wait for deployment (usually 5-10 minutes)

### Step 3: Deploy to Render (Option B - Manual Setup)

If you prefer manual setup or the blueprint doesn't work:

#### 3.1 Create PostgreSQL Database

1. Dashboard → New + → PostgreSQL
2. Name: `file-converter-db`
3. Plan: Free
4. Create Database
5. **Save the Internal Database URL** (you'll need it)

#### 3.2 Create Redis Instance

1. Dashboard → New + → Redis
2. Name: `file-converter-redis`
3. Plan: Free
4. Create Redis
5. **Save the Internal Redis URL**

#### 3.3 Create Web Service

1. Dashboard → New + → Web Service
2. Connect your GitHub repository
3. Configuration:
   - **Name**: `file-converter-web`
   - **Region**: Oregon (US West)
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `daphne -b 0.0.0.0 -p $PORT fileconverter.asgi:application`
   - **Plan**: Free

4. **Environment Variables** (click "Advanced"):
   ```
   PYTHON_VERSION=3.11.0
   DEBUG=False
   SECRET_KEY=<generate-a-random-key>
   DATABASE_URL=<paste-your-postgres-internal-url>
   REDIS_URL=<paste-your-redis-internal-url>
   AWS_ACCESS_KEY_ID=<your-aws-key>
   AWS_SECRET_ACCESS_KEY=<your-aws-secret>
   AWS_STORAGE_BUCKET_NAME=<your-s3-bucket-name>
   AWS_S3_REGION_NAME=us-east-1
   DJANGO_SETTINGS_MODULE=fileconverter.settings_prod
   ```

5. Click "Create Web Service"

#### 3.4 Create Celery Worker Service

1. Dashboard → New + → Background Worker
2. Connect same repository
3. Configuration:
   - **Name**: `file-converter-worker`
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `celery -A fileconverter worker --loglevel=info --pool=solo`
   - **Plan**: Free

4. **Environment Variables**: Same as web service above

5. Click "Create Background Worker"

### Step 4: Make build.sh Executable

If deployment fails with permission error, you may need to make the build script executable:

```bash
chmod +x build.sh
git add build.sh
git commit -m "Make build script executable"
git push
```

### Step 5: Access Your Application

1. Once deployed, go to your web service dashboard
2. You'll see a URL like: `https://file-converter-web.onrender.com`
3. Click it to access your application!

## ⚙️ Configuration Notes

### Environment Variables Explained

- `SECRET_KEY`: Django secret key (generate a secure random string)
- `DEBUG`: Set to `False` for production
- `DATABASE_URL`: PostgreSQL connection string (auto-provided by Render)
- `REDIS_URL`: Redis connection string (auto-provided by Render)
- `AWS_*`: Your AWS S3 credentials
- `DJANGO_SETTINGS_MODULE`: Points to production settings

### Free Tier Limitations

**Render Free Tier**:
- Web service spins down after 15 minutes of inactivity
- First request after inactivity takes 30-60 seconds (cold start)
- 750 hours/month free
- No custom domains on free tier

**Solutions for Cold Starts**:
1. Upgrade to paid tier ($7/month) - services never sleep
2. Use a uptime monitoring service (like UptimeRobot) to ping your app every 10 minutes

### Monitoring Your Application

1. **View Logs**:
   - Go to your service dashboard
   - Click "Logs" tab
   - See real-time logs for debugging

2. **Check Service Health**:
   - Dashboard shows if services are running
   - Green = healthy, Red = issues

3. **Database Access**:
   - PostgreSQL dashboard has connection info
   - Can connect with psql or GUI tools

## 🔧 Updating Your Application

```bash
# Make changes to your code
git add .
git commit -m "Your update message"
git push

# Render automatically detects push and redeploys!
```

## 🐛 Troubleshooting

### Build Fails

**Error**: `Permission denied: ./build.sh`
```bash
chmod +x build.sh
git add build.sh
git commit -m "Fix permissions"
git push
```

**Error**: `Package installation failed`
- Check `requirements.txt` for correct package versions
- Some packages need system dependencies

### Application Won't Start

1. Check Logs in Render dashboard
2. Common issues:
   - Wrong `DJANGO_SETTINGS_MODULE`
   - Missing environment variables
   - Database migration errors

**Fix**: Make sure `DJANGO_SETTINGS_MODULE=fileconverter.settings_prod` is set

### WebSockets Not Working

- Free tier has limitations on WebSocket connections
- Upgrade to paid tier for better WebSocket support
- Check REDIS_URL is correctly configured

### File Upload/Download Issues

1. **Verify S3 Configuration**:
   - Check AWS credentials are correct
   - Verify S3 bucket exists and is accessible
   - Check bucket CORS configuration

2. **Check Logs** for S3 errors:
   - Access denied = wrong credentials or IAM permissions
   - Bucket not found = wrong bucket name or region

### Database Connection Errors

- Verify DATABASE_URL is set correctly
- Check PostgreSQL service is running
- Try running migrations manually via Render shell

### Celery Worker Not Processing Tasks

1. Check worker service is running (Render dashboard)
2. Verify REDIS_URL is same for web and worker
3. Check worker logs for errors

## 💰 Cost Optimization

**Free Tier Setup** (Good for personal/testing use):
- PostgreSQL: Free (256MB)
- Redis: Free (25MB)
- Web Service: Free (750 hours/month)
- Worker: Free (750 hours/month)
- **Total: $0/month** (just pay for S3 storage, usually < $1/month for light use)

**Production Setup** ($17/month):
- PostgreSQL: Free or $7/month (1GB)
- Redis: $7/month (512MB, persistent)
- Web Service: $7/month (no cold starts)
- Worker: Free (or $7/month if heavy processing)
- S3: ~$1-5/month depending on usage

## 🔒 Security Checklist

- ✅ `DEBUG=False` in production
- ✅ Strong `SECRET_KEY` (generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- ✅ AWS credentials with minimal permissions (only S3 access)
- ✅ Enable HTTPS (Render does this automatically)
- ✅ Set up ALLOWED_HOSTS properly
- ✅ Regular backups of PostgreSQL database

## 📱 Post-Deployment Steps

1. **Create a Superuser** (for Django admin):
   ```bash
   # In Render dashboard, open Shell for web service
   python manage.py createsuperuser
   ```

2. **Test All Features**:
   - Upload and convert files
   - Check WebSocket real-time updates
   - Verify downloads work
   - Test conversion history

3. **Set Up Monitoring**:
   - UptimeRobot (free): Keep app awake, get downtime alerts
   - Sentry (optional): Error tracking

4. **Bookmark Your URL**:
   - Add to your browser favorites
   - Create a PWA/app shortcut on mobile

## 🎉 You're Done!

Your file converter is now live and accessible from anywhere! 

**Your app URL**: `https://file-converter-web.onrender.com` (replace with your actual URL)

## 📞 Need Help?

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Django Channels**: [channels.readthedocs.io](https://channels.readthedocs.io)
- **AWS S3**: [docs.aws.amazon.com/s3](https://docs.aws.amazon.com/s3/)

---

**Pro Tip**: For daily use on the free tier, consider:
1. Using [UptimeRobot](https://uptimerobot.com/) to ping your app every 14 minutes to prevent cold starts
2. Setting up a custom domain (requires paid tier)
3. Upgrading to paid tier for instant response times ($7/month)


