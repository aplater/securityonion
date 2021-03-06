#!py

import logging

def status():
    return __salt__['cmd.run']('/usr/sbin/so-status')


def mysql_conn(retry):
    log = logging.getLogger(__name__)

    from time import sleep

    try:
        from MySQLdb import _mysql
    except ImportError as e:
        log.error(e)
        return False

    mainint = __salt__['pillar.get']('sensor:mainint', __salt__['pillar.get']('manager:mainint'))
    mainip = __salt__['grains.get']('ip_interfaces').get(mainint)[0]

    mysql_up = False
    for i in range(0, retry):
        log.debug(f'Connection attempt {i+1}')
        try:
            db = _mysql.connect(
                host=mainip,
                user='root',
                passwd=__salt__['pillar.get']('secrets:mysql')
            )
            log.debug(f'Connected to MySQL server on {mainip} after {i} attempts.')
            
            db.query("""SELECT 1;""")
            log.debug(f'Successfully completed query against MySQL server on {mainip}')
            
            db.close()
            mysql_up = True
            break
        except _mysql.OperationalError as e:
            log.debug(e)
        except Exception as e:
            log.error('Unexpected error occured.')
            log.error(e)
            break
        sleep(1)

    if not mysql_up:
        log.error(f'Could not connect to MySQL server on {mainip} after {retry} attempts.')

    return mysql_up