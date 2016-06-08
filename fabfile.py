from fabric.api import *

env.hosts = ['192.168.17.80']
location = '~/smartgrid'
repo_url = 'https://github.com/kroczi/TIR_energy_flow.git'
cmd = 'python {0}/main.py -n {1} -d 0 -I'

def prerequisties():
    run('yes | sudo apt-get install python-pip')
    run('sudo pip install python-setuptools')

def install():
    global location, repo_url
    run('git clone {0} {1}'.format(repo_url, location))
    run('pip install -e {0} --user'.format(location))

def execute(node_id):
    global location, cmd
    run('nohup {0} > /tmp/smartgrid.log 2>&1 < /dev/null &'.format(cmd.format(location, node_id)), pty=False)

def setup_all():
    prerequisties()
    install()
    execute_all()


def execute_all():
    oldhosts = env.hosts
    for node_id in range(0, len(oldhosts)):
        env.hosts = [oldhosts[node_id]]
        execute(node_id)
    env.hosts = oldhosts

def reboot_all():
    run('reboot -f')