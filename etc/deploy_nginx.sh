#!/usr/bin/env bash
# deploy_nginx.sh
# Sao chép config từ repo -> /etc/nginx/sites-available,
# bật symlink trong sites-enabled, disable default, kiểm tra và reload nginx.
set -euo pipefail

CONFIG_NAME="llm_gateway.conf"
SRC_PATH="./etc/nginx/sites-available/$CONFIG_NAME"
DEST_AVAILABLE="/etc/nginx/sites-available/$CONFIG_NAME"
DEST_ENABLED="/etc/nginx/sites-enabled/$CONFIG_NAME"
DEFAULT_ENABLED="/etc/nginx/sites-enabled/default"

# Kiểm tra file nguồn trong repo
if [ ! -f "$SRC_PATH" ]; then
  echo "Lỗi: Không tìm thấy file nguồn: $SRC_PATH"
  exit 1
fi

echo "--- 1. Copy config lên /etc/nginx/sites-available/ ---"
sudo cp "$SRC_PATH" "$DEST_AVAILABLE"
sudo chown root:root "$DEST_AVAILABLE"
sudo chmod 644 "$DEST_AVAILABLE"
echo "Đã copy -> $DEST_AVAILABLE"

echo "--- 2. Tạo hoặc cập nhật symlink trong sites-enabled/ ---"
if [ -L "$DEST_ENABLED" ]; then
  echo "Đã tồn tại symlink $DEST_ENABLED — cập nhật (nếu cần)..."
  sudo ln -sf "$DEST_AVAILABLE" "$DEST_ENABLED"
else
  echo "Tạo symlink $DEST_ENABLED -> $DEST_AVAILABLE"
  sudo ln -s "$DEST_AVAILABLE" "$DEST_ENABLED"
fi

echo "--- 3. Vô hiệu hóa site mặc định (nếu có) ---"
if [ -e "$DEFAULT_ENABLED" ] || [ -L "$DEFAULT_ENABLED" ]; then
  echo "Xóa $DEFAULT_ENABLED"
  sudo rm -f "$DEFAULT_ENABLED"
else
  echo "Không tìm thấy default, bỏ qua."
fi

echo "--- 4. Kiểm tra cấu hình nginx ---"
sudo nginx -t

echo "--- 5. Reload nginx (cố gắng reload trước, nếu không thì restart) ---"
if systemctl is-active --quiet nginx; then
  sudo systemctl reload nginx
else
  sudo systemctl restart nginx
fi

echo "Hoàn tất. Nginx đã được cập nhật với $CONFIG_NAME"