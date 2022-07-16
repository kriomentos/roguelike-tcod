class Impossible(Exception):
    '''raise when action taken is impossible to be performed'''

class QuitWithoutSaving(SystemExit):
    '''raised to exit game without autmatically saving'''