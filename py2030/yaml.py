import socket

print 'py2030:'
print '  profiles:'
print '    ' + socket.gethostname().replace('.', '_') + ':'
print "      start_event: 'start'"
