#!./bin/python3

import subprocess
import sys
import re
import datetime
import time
import pprint

DEBUG = True
INFO = True
WARN = True

class DebugPrinter():
    def print_info(*ss):
        if INFO:
            for s in ss:
                print(str(datetime.datetime.now()) + ' [INFO]: ' + str(s))

    def print_warn(*ss):
        if WARN:
            for s in ss:
                print(str(datetime.datetime.now()) + ' [WARN]: ' + str(s))

    def print_debug(*ss):
        if DEBUG:
            for s in ss:
                print(str(datetime.datetime.now()) + ' [DEBUG]: ' + str(s))

print_info = DebugPrinter.print_info
print_warn = DebugPrinter.print_warn
print_debug = DebugPrinter.print_debug

class MonitorStateMachine:
    _identifier = 'main'
    _current_state = 'initializing'
    _valid_states = ['initializing', 'no_clients_alive', 'at_least_one_client_alive']
    _valid_events = ['ping_success', 'ping_timeout']
    _last_state_transition = 'Never'

    def __init__(self, name):
        self._identifier = name

    def __repr__(self):
        return ("MonitorStateMachine(name=%r,curr_state=%r,lasttransition=%r)" %
                (self._identifier,self._current_state,self._last_state_transition))

    def new_event(self, event, client_sm_list):
        if event not in self._valid_events:
            raise(ValueError("Invalid event: "
                + str(current_state)
                + '.'))
            return
        if len(client_sm_list) is 0:
            raise(ValueError("Client SM list is empty"))
            return
        if event is 'ping_success':
            if self._current_state is 'initializing':
                self._last_state_transition = datetime.datetime.now()
                print_info('Monitor '
                        + self._identifier
                        + ' initial state is at_least_one_client_alive.')
            elif self._current_state is 'no_clients_alive':
                self._last_state_transition = datetime.datetime.now()
                print_info('Monitor '
                        + self._identifier
                        + ' went from no clients to at least one client alive.')
            elif self._current_state is 'at_least_one_client_alive':
                pass
            self._current_state = 'at_least_one_client_alive'
            return
        elif event is 'ping_timeout':
            for client_sm in client_sm_list:
                client_state = client_sm.get_current_state()
                if client_state is 'unknown':
                    # cannot change overall state until state of all clients known
                    return
                if client_state is 'alive':
                    # if at least one client is still alive, there will be no
                    # change of state
                    return
            # No clients are responding
            if self._current_state is 'initializing':
                self._last_state_transition = datetime.datetime.now()
                print_info('Monitor '
                        + self._identifier
                        + ' initial state is no_clients_alive.')
            elif self._current_state is 'at_least_one_client_alive':
                self._last_state_transition = datetime.datetime.now()
                print_info('Monitor '
                        + self._identifier
                        + ' went from at_least_one_client_alive to no_clients_alive.')
            elif self._current_state is 'no_clients_alive':
                pass
            self._current_state = 'no_clients_alive'
            return            


class ClientStateMachine:
    _current_state = 'unknown'
    _ip_address = ''
    _valid_states = ['unknown', 'alive', 'not_responding']
    _valid_events = ['ping_success', 'ping_timeout']
    _last_seen = 'Never'

    def __init__(self, ip_address):
        self._ip_address = ip_address

    def __repr__(self):
        return ("ClientStateMachine(ip_address=%r,curr_state=%r,lastseen=%r)" %
                (self._ip_address,self._current_state,self._last_seen))

    def new_event(self, event):
        if event not in self._valid_events:
            raise(ValueError("Invalid event: " 
                + str(current_state) 
                + '.'))
            return
        if event is 'ping_success':
            self._last_seen = datetime.datetime.now()
            if self._current_state is 'unknown':
                print_info('Client ' 
                        + self._ip_address 
                        + ' initial state is alive.')
            elif self._current_state is 'not_responding':
                print_info('Client ' 
                        + self._ip_address 
                        + ' was state not_responding but is now state alive.')
            elif self._current_state is 'alive':
                pass
            self._current_state = 'alive'
            return
        elif event is 'ping_timeout':
            if self._current_state is 'unknown':
                print_info('Client '
                        + self._ip_address
                        + ' initial state is not_responding.')
            elif self._current_state is 'alive':
                print_info('Client '
                        + self._ip_address
                        + ' was state alive but is now state not_responding.')
            elif self._current_state is 'not_responding':
                pass
            self._current_state = 'not_responding'
            return
        
    def get_current_state(self):
        return self._current_state

    def get_last_seen(self):
        return self._last_seen

    def get_ip(self):
        return self._ip_address


def is_alive(ip_address):
    # needs root
    cmd = 'arping -c 10 -C 1 -D ' + ip_address
    try:
        s = subprocess.run(cmd.split(),
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)
    except FileNotFoundError:
        # exit with status 1 (fail)
        sys.exit('Error: Could not find ' + cmd_list[0] + '.')

    if re.search(r'!',s.stdout.decode()):
        return True
    else:
        return False


if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=4)
    # TODO: make cli args
    minimum_polling_interval_in_secs = 60
    client_ip_addresses = ['10.0.1.21',
              '10.0.1.26',
              ]
    print_info('Client list: \n' + pp.pformat(client_ip_addresses))
    print_info('Min polling interval (secs): ' 
            + str(minimum_polling_interval_in_secs))
    # initialize monitor (overall) state machine
    monitor_sm = MonitorStateMachine('main')
    # initialize client state machines
    client_state_machines = []
    for ip in client_ip_addresses:
        client_state_machines.append(ClientStateMachine(ip))

    while (1):
        try:
            start_of_polling_interval = datetime.datetime.now()
            for client_sm in client_state_machines:
                if is_alive(client_sm.get_ip()):
                    client_sm.new_event('ping_success')
                    monitor_sm.new_event('ping_success',client_state_machines)
                else:
                    client_sm.new_event('ping_timeout')
                    monitor_sm.new_event('ping_timeout',client_state_machines)

            # sleep enough to satisfy minimum polling interval
            # if doing arp pings has taken longer than the min polling interval, 
            # then start the next polling interval immediately
            time_diff = datetime.datetime.now() - start_of_polling_interval
            min_polling_interval = datetime.timedelta(seconds=minimum_polling_interval_in_secs)
            if (time_diff > min_polling_interval):
                continue
            else:
                sleep_time = min_polling_interval - time_diff
                time.sleep(sleep_time.total_seconds())
        except KeyboardInterrupt:
            print_debug(pp.pformat(client_state_machines) 
                    + '\n\n'
                    + pp.pformat(monitor_sm))
            sys.exit(0)
