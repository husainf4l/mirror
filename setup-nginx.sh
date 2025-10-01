#!/bin/bash

# Setup script for nginx SSL configuration for oya36.com

echo "Setting up nginx SSL configuration for oya36.com..."

# 1. Copy nginx configuration
sudo cp oya36.com.nginx.conf /etc/nginx/sites-available/oya36.com

# 2. Enable the site
sudo ln -sf /etc/nginx/sites-available/oya36.com /etc/nginx/sites-enabled/

# 3. Remove default nginx site if it exists
sudo rm -f /etc/nginx/sites-enabled/default

# 4. Test nginx configuration
echo "Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "Nginx configuration is valid"
    
    # 5. Install certbot if not already installed
    echo "Installing certbot for SSL certificates..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
    
    # 6. Get SSL certificate
    echo "Obtaining SSL certificate for oya36.com..."
    sudo certbot --nginx -d oya36.com -d www.oya36.com --non-interactive --agree-tos --email husain@oya36.com
    
    # 7. Reload nginx
    echo "Reloading nginx..."
    sudo systemctl reload nginx
    
    # 8. Enable nginx to start on boot
    sudo systemctl enable nginx
    
    echo "Setup complete!"
    echo "Your mirror application should now be accessible at https://oya36.com"
    echo ""
    echo "Make sure your FastAPI application is running on port 8000:"
    echo "uvicorn main:app --host 0.0.0.0 --port 8000"
    
else
    echo "Nginx configuration has errors. Please check the configuration file."
    exit 1
fi
