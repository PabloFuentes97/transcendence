#! /bin/sh

mkdir -p /etc/nginx/ssl/
chmod -R 700 /etc/nginx/ssl/
if [ ! -f /etc/nginx/ssl/private_key.pem ]; then
        openssl genpkey -algorithm RSA -out /etc/nginx/ssl/private_key.pem > /dev/null 2>&1
        echo "Private key generated."
fi

if [ ! -f /etc/nginx/ssl/cert.pem ]; then
        openssl req -new -x509 -key /etc/nginx/ssl/private_key.pem -out /etc/nginx/ssl/cert.pem -days 365 \
            -subj "$CERT_DETAILS" > /dev/null 2>&1
        echo "TLS certificate generated."
fi

echo "Starting NGINX"

nginx -g "daemon off;"