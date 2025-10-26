# 🚀 Multi-Format File Converter

A powerful, modern web application built with Django that converts files between multiple formats. Features real-time progress updates via WebSockets, asynchronous processing with Celery, and a beautiful, responsive UI.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/django-4.2+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- **Multiple Format Support**
  - 📷 **Images**: JPG, PNG, GIF, BMP, WebP, TIFF, PDF
  - 📄 **Documents**: PDF, DOCX, TXT
  - 🎥 **Videos**: MP4, AVI, GIF

- **Real-time Progress Updates** via WebSockets
- **Asynchronous Processing** with Celery
- **Beautiful Modern UI** with smooth animations
- **Drag & Drop** file upload
- **File History** tracking
- **RESTful API** for programmatic access

## 🛠️ Technology Stack

- **Backend**: Django 4.2+
- **Task Queue**: Celery
- **Message Broker**: Redis
- **WebSockets**: Django Channels + Daphne
- **Image Processing**: Pillow, OpenCV
- **Document Processing**: PyPDF2, pdf2docx, python-docx
- **Video Processing**: MoviePy
- **Frontend**: Vanilla JavaScript, CSS3, HTML5

## 📋 Prerequisites

- Python 3.9 or higher
- Redis Server
- Git

### Windows Additional Requirements
- Visual C++ Build Tools (for some Python packages)

### Linux Additional Requirements
```bash
sudo apt-get update
sudo apt-get install -y python3-dev build-essential redis-server
```

### macOS Additional Requirements
```bash
brew install redis
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd file-converter
```

### 2. Create Virtual Environment

```bash
# Windows
py -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Django

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate



# Collect static files (for production)
python manage.py collectstatic --noinput
```

### 5. Start Services

You'll need **3 terminal windows**:

#### Terminal 1: Start Redis
```bash
# Windows (if installed as service)
redis-server

# Linux/macOS
redis-server

# Or if installed as Windows service
net start redis
```

#### Terminal 2: Start Celery Worker
```bash
# Activate virtual environment first
celery -A fileconverter worker --loglevel=info

# Windows users might need:
celery -A fileconverter worker --pool=solo --loglevel=info
```

#### Terminal 3: Start Django Server
```bash
# For development with WebSocket support
daphne -b 127.0.0.1 -p 8000 fileconverter.asgi:application

# Or use Django development server (WebSockets won't work)
python manage.py runserver
```

### 6. Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

## 📁 Project Structure

```
file-converter/
├── fileconverter/          # Main project directory
│   ├── __init__.py
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   ├── asgi.py             # ASGI config for WebSockets
│   ├── wsgi.py             # WSGI config
│   └── celery.py           # Celery configuration
├── converter/              # Main app directory
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # App URL patterns
│   ├── tasks.py            # Celery tasks
│   ├── utils.py            # Conversion utilities
│   ├── forms.py            # Django forms
│   ├── consumers.py        # WebSocket consumers
│   ├── routing.py          # WebSocket routing
│   └── admin.py            # Admin interface
├── templates/              # HTML templates
│   └── converter/
│       ├── base.html       # Base template
│       ├── index.html      # Home page
│       └── convert.html    # Conversion page
├── media/                  # Uploaded & converted files
│   ├── uploads/
│   └── converted/
├── static/                 # Static files (CSS, JS, images)
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:password@localhost/dbname

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

### settings.py Configuration

Key settings in `fileconverter/settings.py`:

```python
# Maximum upload size (100MB)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024

# Celery broker URL
CELERY_BROKER_URL = 'redis://localhost:6379/0'

# Channels layer for WebSockets
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

## 📝 API Endpoints

### Upload File
```http
POST /api/upload/
Content-Type: multipart/form-data

Parameters:
- file: File to convert
- target_format: Target format (e.g., "pdf", "jpg")
- conversion_type: Type ("image", "document", or "video")

Response:
{
  "success": true,
  "conversion_id": "uuid",
  "message": "File uploaded successfully"
}
```

### Check Status
```http
GET /api/status/<conversion_id>/

Response:
{
  "id": "uuid",
  "status": "completed",
  "original_filename": "example.jpg",
  "original_format": "jpg",
  "target_format": "png",
  "download_url": "/api/download/<uuid>/"
}
```

### Download File
```http
GET /api/download/<conversion_id>/

Returns: Converted file
```

### Conversion History
```http
GET /api/history/?limit=10

Response:
{
  "conversions": [
    {
      "id": "uuid",
      "original_filename": "example.jpg",
      "status": "completed",
      ...
    }
  ]
}
```

### Delete Conversion
```http
POST /api/delete/<conversion_id>/

Response:
{
  "success": true,
  "message": "Conversion deleted successfully"
}
```

## 🎨 Supported Conversions

### Image Conversions
- JPG ↔ PNG, GIF, BMP, WebP, TIFF
- PNG ↔ JPG, GIF, BMP, WebP
- Any image → PDF

### Document Conversions
- PDF → DOCX, TXT, JPG, PNG
- DOCX → PDF, TXT
- TXT → PDF

### Video Conversions
- MP4 → GIF, AVI
- AVI, MOV, MKV → MP4

## 🐳 Docker Deployment

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  web:
    build: .
    command: daphne -b 0.0.0.0 -p 8000 fileconverter.asgi:application
    volumes:
      - ./media:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
  
  celery:
    build: .
    command: celery -A fileconverter worker --loglevel=info
    volumes:
      - ./media:/app/media
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
```

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "fileconverter.asgi:application"]
```

Run with:
```bash
docker-compose up -d
```

## 🔒 Security Considerations

### Production Checklist

1. **Change SECRET_KEY** in settings.py
2. **Set DEBUG = False**
3. **Configure ALLOWED_HOSTS**
4. **Use environment variables** for sensitive data
5. **Enable HTTPS**
6. **Set up CORS** if using API from different domain
7. **Implement rate limiting**
8. **Add authentication** for API endpoints
9. **Regular cleanup** of old files

### File Size Limits

Current limit: **100MB**

To change, modify in `settings.py`:
```python
MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200MB
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE
```

## 🐛 Troubleshooting

### Redis Connection Error
```
Error: Redis connection refused
```
**Solution**: Make sure Redis is running
```bash
redis-server
# or
net start redis  # Windows service
```

### Celery Not Processing Tasks
```bash
# Check if celery worker is running
celery -A fileconverter worker --loglevel=debug
```

### WebSocket Connection Failed
- Make sure you're using Daphne: `daphne -b 127.0.0.1 -p 8000 fileconverter.asgi:application`
- Check if channels and channels-redis are installed
- Verify Redis is running

### ImportError for pdf2image
```
PDFInfoNotInstalledError: Unable to get page count
```
**Solution**: Install poppler
```bash
# Windows: Download from https://github.com/oschwartz10612/poppler-windows
# Add to PATH

# Linux
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

### Video Conversion Fails
**Solution**: Install FFmpeg
```bash
# Windows: Download from https://ffmpeg.org/
# Add to PATH

# Linux
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

## 📊 Monitoring & Logs

### View Celery Tasks
```bash
celery -A fileconverter events
```

### Flower (Celery Monitoring)
```bash
pip install flower
celery -A fileconverter flower
# Access at http://localhost:5555
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django team for the amazing framework
- Celery for async task processing
- All open-source libraries used in this project

## 📧 Support

For support, email support@example.com or open an issue on GitHub.

## 🔄 Updates & Roadmap

### Coming Soon
- [ ] Batch file conversion
- [ ] User authentication & file history
- [ ] API rate limiting
- [ ] More format support
- [ ] Preview generation
- [ ] Cloud storage integration (AWS S3, Google Drive)
- [ ] OCR for PDF/Image to text
- [ ] Compression options

---

Made with ❤️ using Django, Celery, and WebSockets

