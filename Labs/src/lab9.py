import io
from fabric import Connection

EC2_HOST = '52.199.197.18'
KEY_FILE = '../23011392-key.pem'


def setup_django_app():
    c = Connection(EC2_HOST, user='ubuntu', connect_kwargs={"key_filename": KEY_FILE})

    # Update and upgrade
    c.sudo('apt-get update')
    c.sudo('apt-get upgrade -y')

    # Try to fix broken packages
    c.sudo('apt --fix-broken install')

    # Try to install python3-venv
    try:
        c.sudo('apt-get install -y python3-venv')
    except:
        try:
            c.sudo('apt install -y python3-venv')
        except:
            print("Failed to install python3-venv. Proceeding without explicit installation.")

    # The rest of your function remains the same
    # Step 3: Create and access directory
    c.sudo('mkdir -p /opt/wwc/mysites')
    c.sudo('chown ubuntu:ubuntu /opt/wwc/mysites')

    with c.cd('/opt/wwc/mysites'):
        # Step 4: Set up virtual environment
        c.run('python3 -m venv myvenv')

        # Step 5: Activate virtual environment and set up Django
        c.run('source myvenv/bin/activate && pip install django')
        c.run('source myvenv/bin/activate && django-admin startproject lab')
        c.run('cd lab && source ../myvenv/bin/activate && python3 manage.py startapp polls')

    # Step 6: Install nginx
    c.sudo('apt install nginx -y')

    # Step 7: Configure nginx
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
    c.put(io.StringIO(nginx_config), '/tmp/nginx_config')
    c.sudo('mv /tmp/nginx_config /etc/nginx/sites-available/default')

    # Step 8: Restart nginx
    c.sudo('service nginx restart')

    # Set up Django inside the created EC2 instance
    # Step 1: Edit Django files
    polls_views = '''
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world.")
'''
    c.put(io.StringIO(polls_views), '/opt/wwc/mysites/lab/polls/views.py')

    polls_urls = '''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
'''
    c.put(io.StringIO(polls_urls), '/opt/wwc/mysites/lab/polls/urls.py')

    lab_urls = '''
from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]
'''
    c.put(io.StringIO(lab_urls), '/opt/wwc/mysites/lab/urls.py')



if __name__ == "__main__":
    setup_django_app()