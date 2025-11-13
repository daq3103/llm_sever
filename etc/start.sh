set -e

cd ..

echo "--- 2. Cấu hình Nginx... ---"
sudo cp ./etc/nginx/sites-available/llm_gateway.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/llm_gateway.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

echo "--- 3. Khởi động Nginx... ---"
sudo nginx