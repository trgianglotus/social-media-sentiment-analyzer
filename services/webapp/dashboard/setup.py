import subprocess
s = subprocess.check_output('grep "^A" %s | grep TYR || true' % 'manage.py', shell = True).split('\n')


print(s)