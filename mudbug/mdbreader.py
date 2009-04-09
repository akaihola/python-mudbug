from os import popen

def mdb_action(action, mdbpath, table='', options=''):
    table = table and ' "%s"' % table
    cmd = 'mdb-%(action)s %(options)s %(mdbpath)s%(table)s' % locals()
    return popen(cmd)
