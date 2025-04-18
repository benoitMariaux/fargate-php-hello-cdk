FROM --platform=linux/amd64 php:8.2-apache

COPY index.php /var/www/html/

# Add security headers for CloudFront
RUN echo 'ServerTokens Prod' >> /etc/apache2/apache2.conf && \
    echo 'ServerSignature Off' >> /etc/apache2/apache2.conf && \
    a2enmod headers && \
    echo 'Header set X-Content-Type-Options "nosniff"' >> /etc/apache2/apache2.conf && \
    echo 'Header set X-Frame-Options "SAMEORIGIN"' >> /etc/apache2/apache2.conf && \
    echo 'Header set X-XSS-Protection "1; mode=block"' >> /etc/apache2/apache2.conf

EXPOSE 80

CMD ["apache2-foreground"]
