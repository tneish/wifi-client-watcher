# wifi-client-watcher
Tested with Python 3.5 and [ARPing](https://linux.die.net/man/8/arping) 2.14.

ARPing is available in many Linux distribution repositories, and in the OpenBSD ports tree.

e.g.
`$ sudo apt-get install arping`

Edit `wifi-client-watcher-arping.py` and update list of IP addresses, and (optionally) minimum poll time. If the script should do more than simply print changes to stdout, you can update in the appropriate places in the script.

Since ARPing needs CAP_NET_RAW privileges, it should be run as root:

```
$ sudo ./wifi-client-watcher-arping.py
2018-07-16 00:27:19.677155 [INFO]: Client list:
['127.0.0.1', '10.0.1.25', '10.0.1.123', '10.0.1.21', '10.0.1.26']
2018-07-16 00:27:19.677192 [INFO]: Min polling interval (secs): 60
2018-07-16 00:27:30.266756 [INFO]: Client 127.0.0.1 initial state is not_responding.
2018-07-16 00:27:30.398506 [INFO]: Client 10.0.1.25 initial state is alive.
2018-07-16 00:27:30.398649 [INFO]: Monitor main initial state is at_least_one_client_alive.
2018-07-16 00:27:40.490575 [INFO]: Client 10.0.1.123 initial state is not_responding.
2018-07-16 00:27:50.590611 [INFO]: Client 10.0.1.21 initial state is not_responding.
2018-07-16 00:27:58.766550 [INFO]: Client 10.0.1.26 initial state is alive.
2018-07-16 00:29:43.602562 [INFO]: Client 10.0.1.21 was state not_responding but is now state alive.
```


