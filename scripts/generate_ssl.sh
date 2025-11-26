#!/bin/bash
# Generate self-signed SSL certificates for FoodFlow

mkdir -p certs

# Generate private key
openssl genrsa -out certs/server.key 2048

# Generate certificate signing request
openssl req -new -key certs/server.key -out certs/server.csr -subj "/C=FR/ST=Occitanie/L=Montpellier/O=FoodFlow/OU=IT/CN=swautomorph.com"

# Generate self-signed certificate
openssl x509 -req -days 365 -in certs/server.csr -signkey certs/server.key -out certs/server.crt

# Set permissions
chmod 600 certs/server.key
chmod 644 certs/server.crt

echo "✅ SSL certificates generated in certs/ directory"
echo "   • Private key: certs/server.key"
echo "   • Certificate: certs/server.crt"