import dreampylib
import config

if __name__ == '__main__':
    connection = dreampylib.DreampyLib(config.user, config.key)
    if connection.IsConnected():
        print('Available commands:\n')
        commands = connection.AvailableCommands()
        print('\n '.join([x[0] for x in commands]))
