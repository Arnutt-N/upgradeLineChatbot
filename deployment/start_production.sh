#!/bin/bash
# Production Deployment Script for Render.com
# This script ensures the application is ready for production

echo "🚀 Starting Production Deployment..."
echo "============================================"

# Check Python version
echo "🐍 Python version:"
python --version

# Install dependencies with timeout
echo "📦 Installing dependencies..."
pip install --upgrade pip --timeout 120
pip install -r requirements.txt --timeout 300

# Run database migration
echo "🗄️ Running database migration..."
python deployment/migrate_production.py

# Verify critical files exist
echo "📁 Verifying critical files..."
files=(
    "app/main.py"
    "app/core/config.py" 
    "app/db/database.py"
    "requirements.txt"
    "render.yaml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Check environment variables
echo "🔧 Checking environment variables..."
required_vars=(
    "ENVIRONMENT"
    "LINE_CHANNEL_SECRET"
    "LINE_CHANNEL_ACCESS_TOKEN"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    else
        echo "✅ $var is set"
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "⚠️ Missing environment variables:"
    printf "   - %s\n" "${missing_vars[@]}"
    echo ""
    echo "📋 Please set these in Render Dashboard:"
    echo "   Dashboard > Your Service > Environment"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p temp

# Set proper permissions
echo "🔐 Setting permissions..."
chmod +x deployment/migrate_production.py
chmod +x deployment/start_production.sh

echo ""
echo "============================================"
echo "🎉 Production deployment preparation complete!"
echo ""
echo "🌐 Your application will be available at:"
echo "   https://your-app-name.onrender.com"
echo ""
echo "📋 Next steps:"
echo "   1. Set environment variables in Render Dashboard"
echo "   2. Update LINE webhook URL"
echo "   3. Test all endpoints"
echo ""
echo "✅ Ready for production!"
