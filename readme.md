# Check ISV status RLM Licence server

Check the status of a license ISV on rlm license server using rlmutil command

## Where get the rlmutil

https://reprisesoftware.com/support/admin/license-administration-bundle/

## What to do this script

```bash
$ rlmutil rlmstat -c 5053@srvdf2.uab.cat -a -i simio

Setting license file path to 5053@srvdf2.uab.cat
rlmutil v15.1
Copyright (C) 2006-2022, Reprise Software, Inc. All rights reserved.


        ------------------------

        simio ISV server status on srvdf2.uab.cat (port 49827), up 3d 20:11:13
        simio software version v15.1 (build: 1)
        simio comm version: v1.2
        simio info log filename: C:\ProgramData\Simio LLC\Simio Network Licensing\simio.dlog
        simio Report log filename: <stdout>
        Startup time: Thu May 16 12:30:10 2024
        Todays Statistics (08:40:33), init time: Mon May 20 00:00:50 2024
        Recent Statistics (00:01:59), init time: Mon May 20 08:39:24 2024

                     Recent Stats         Todays Stats         Total Stats
                      00:01:59             08:40:33          3d 20:11:13
        Messages:    8 (0/sec)           52 (0/sec)          40541 (0/sec)
        Connections: 4 (0/sec)           26 (0/sec)          833 (0/sec)
        Checkouts:   0 (0/sec)           0 (0/sec)          365 (0/sec)
        Denials:     0 (0/sec)           0 (0/sec)          0 (0/sec)
        Removals:    0 (0/sec)           0 (0/sec)          0 (0/sec)


        ------------------------

        simio license pool status on srvdf2.uab.cat (port 49827)

        simio-academic v2025.01, pool: 1
                count: 100, # reservations: 0, inuse: 0, exp: 09-jan-2025
                obsolete: 0, min_remove: 120, total checkouts: 0

```

with the stdoutput we use a regexp to capture the 
- ISV
- SERVER
- PORT
- Software name
- Pool
- Count
- Reservations
- In Use
- Expiration

and check the requirements

## Usage

```data
usage: /home/jroman/Descargas/rlm/./check_rlm.py [-h] -H SERVER -P PORT -i ISV -l NUM_LIC -w WARN_LIC -c CRIT_LIC -W WARN_EXPIRATION -C CRIT_EXPIRATION [-p RLMUTIL]

Check the state of a ISV server on rlm license server.

options:
  -h, --help          show this help message and exit
  -H SERVER           Server Name or IP
  -P PORT             Port of service
  -i ISV              ISV name
  -l NUM_LIC          Number of licences.
  -w WARN_LIC         Number of licences used for warning.
  -c CRIT_LIC         Number of licences used for critical.
  -W WARN_EXPIRATION  Days to expiration for warning.
  -C CRIT_EXPIRATION  Days to expiration for critical.
  -p RLMUTIL          rlmutil path.

2024(JRM - UAB - SID SBD)
```
