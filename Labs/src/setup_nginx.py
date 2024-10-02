from fabric import Connection, task
import io

c = Connection('23011392-vm')


@task
def setup_django_app(c):
    """"""

    # Update and install required packages
    c.sudo('apt-get update')
    c.sudo('apt-get upgrade -y')
    c.sudo('apt-get install -y python3-venv nginx')

    # Ensure directory exists and has correct permissions
    c.sudo('mkdir -p /opt/wwc/mysites')
    c.sudo('chown -R ubuntu:ubuntu /opt/wwc/mysites')

    with c.cd('/opt/wwc/mysites'):
        c.run('python3 -m venv myvenv')
        c.run('source /opt/wwc/mysites/myvenv/bin/activate && python3 manage.py startapp polls')
        c.run('pip install django')
        c.run('django-admin startproject lab')
        with c.cd('lab'):
            c.run('python3 manage.py startapp polls')

    # Configure and start nginx
    c.sudo('systemctl start nginx')
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
    config_file = io.StringIO(nginx_config)
    c.put(config_file, '/tmp/nginx_config')
    c.sudo('mv /tmp/nginx_config /etc/nginx/sites-available/default')
    c.sudo('systemctl restart nginx')

    print("Nginx has been installed and configured.")


if __name__ == '__main__':
    setup_django_app(c)
