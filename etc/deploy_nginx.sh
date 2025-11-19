#!/bin/bash
CONFIG_NAME="llm_gateway.conf"

AVAILABLE_PATH="/etc/nginx/sites-available/$CONFIG_NAME"
ENABLED_PATH="/etc/nginx/sites-enabled/$CONFIG_NAME"
DEFAULT_PATH="/etc/nginx/sites-enabled/default"

set -e

if [ ! -f "$AVAILABLE_PATH" ]; then
    echo "Lỗi: Không tìm thấy file config tại $AVAILABLE_PATH"
    exit 1
fi

if [ -L "$ENABLED_PATH" ]; then
    echo "Thông báo: Config $CONFIG_NAME đã được kích hoạt."
else
    echo "Kích hoạt $CONFIG_NAME..."
    sudo ln -s "$AVAILABLE_PATH" "$ENABLED_PATH"
fi

if [ -L "$DEFAULT_PATH" ]; then
    echo "Vô hiệu hóa config Nginx mặc định..."
    sudo rm "$DEFAULT_PATH"
else
    echo "Thông báo: Config mặc định đã được vô hiệu hóa."
fi

echo "Kiểm tra cú pháp Nginx..."
sudo nginx -t

echo "Khởi động lại Nginx..."
sudo systemctl restart nginx

echo "Hoàn tất! Nginx đã được cập nhật với $CONFIG_NAME."