import io

from fabric import Connection


c = Connection('23011392-vm1')


def setup_nginx(c):
    """"""

    # Update the packet list
    c.sudo('apt-get update')

    # Install nginx
    c.sudo('apt-get install -y nginx')

    # Start nginx service
    c.sudo('systemctl start nginx')

    # Enable nginx to start on boot
    c.sudo('systemctl enable nginx')

    # Configure nginx
    nginx_config = '''
       server {
          listen 80 default_server;
          listen [::]:80 default_server;
        
          location / {
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        
            proxy_pass http://127.0.0.1:8000;
          }
        }
       '''

    # Write the nginx configuration, using io.StringIO to create an object with config,
    # using Fabric's put method to upload this configuration to a temporary file on the EC2 instance.
    config_file = io.StringIO(nginx_config)
    c.put(config_file, '/tmp/nginx_config')
    c.sudo('mv /tmp/nginx_config /etc/nginx/sites-available/default')

    # Restart nginx to apply changes
    c.sudo('systemctl restart nginx')

    print("Nginx has been installed and configured.")


if __name__ == '__main__':
    setup_nginx(c)