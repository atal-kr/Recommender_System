import datetime
import os
import time

from fabric.api import *

def start_service(apache_service):
    sudo("service %s start" % apache_service)
    sudo("/etc/init.d/supervisor start")
    sudo("/etc/init.d/celeryd start")
    sudo("/etc/init.d/celerybeat start")

def stop_service(apache_service):
    sudo("service %s stop" % apache_service)
    try:
        sudo("/etc/init.d/celeryd stop")
        sudo("/etc/init.d/celerybeat stop")
    except Exception as e:
        print( "Exception: %s" % e)
        print ("Continuing..")

def deploy(install_config="yes", apache_service="apache2", ssl_only="no"):
    print ("Deploying  Recommender service. install_config: %s, apache service name: %s" % (install_config, apache_service))
    now = datetime.datetime.now()
    #local_tmp_dir = os.path.join("/tmp/recommender_service", now.isoformat())
    #local_archive = os.path.join(local_tmp_dir, "recommender_service.tar.gz")
    # local("mkdir -p %s" % local_tmp_dir)
    # local("git archive --format=tar --prefix=recommender_service/ HEAD | gzip > %s" % local_archive)

    #sudo("rm -f /tmp/recommender_service.tar.gz")
    # put(local_archive, "/tmp/")
    stop_service(apache_service)
    sudo("rm -rf /opt/recommender/recommender_service")
    sudo("mkdir -p /opt/recommender/")
    # Create virtualenv
    sudo("virtualenv /opt/pyenv/myplex3.5")
    # with cd("/opt/"):
    #     sudo("tar xf /tmp/recommender_service.tar.gz")
    with prefix(". /opt/pyenv/myplex3.5/bin/activate"):
        with cd("/opt/recommender/recommender_service"):
            run('echo "installing python packages for `which python`"')
            sudo("pip install -r requirements.txt")
            sudo("python manage.py makemigrations --fake-initial")
            #sudo("python manage.py migrate recommendation")
            sudo("python manage.py migrate")
            # clear cache
            #sudo("python manage.py clear_cache")
            # create admin user
            #sudo("python manage.py create_admin")
            # static files
            # sudo("python manage.py collectstatic --noinput")
            # sudo("rm -rf /var/www/recommender_service/static")
            # sudo("mkdir -p /var/www/recommender_service/static")
            # sudo("cp -r static/* /var/www/recommender_service/static/")
            #sudo("cp -r staticgen/* /var/www/recommender_service/static/")

            # Deploy config
            if install_config != 'no':
                apache_conf_dir = "/etc/%s/sites-enabled/" % apache_service
                sudo("cp conf/apache_recommender_service.conf %s" % apache_conf_dir)

            else:
                print ("Not deploying Apache config")
    # Wait for a while
    time.sleep(2)
    start_service(apache_service)
    # run("rm /tmp/recommender_service.tar.gz")
    # local("rm -r %s" % local_tmp_dir)

