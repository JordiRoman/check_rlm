#!/usr/bin/env python3

import os, sys, logging
import argparse
import subprocess, shutil
import re
from datetime import datetime


VERSION="0.0"

NAGIOS_OK=0
NAGIOS_WARN=1
NAGIOS_CRIT=2
NAGIOS_UNKNOWN=3

"""
Script para interrogar a un servidor de licencias RLM
    https://realityserver.com/rlm-licensing-installation/

Dependencias:
    Necesitamos el comando externo rlmutil
    Podemos indicar la ubicacion con  
    https://reprisesoftware.com/support/admin/license-administration-bundle/

Que debe mirar:

    rlmutil rlmstat -c 5053@srvdf2.uab.cat -a -i simio

    El estado del servidor de licencias para un isv concreto
    - puerto   : 5053
    - servidor : srvdf2.uab.cat
    - isv: simio
    - numero de licencias esperadas: 100
    - licencia warning : numero de licencias en uso > : 50
    - licencia critical: numero de licencias en uso > : 90
    - caducidad warning: numero de dias hasta caducidad < : 30
    - caducidad critical: numero de dias hasta caducidad < : 10

=== Ejemplo de STDOUT ===
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

=== END ===

"""

def parse_args (argv):
    """
    Funcion que parsea los argumentos de la linea de comandos
    
    Argumentos:
        argv: array de argumentos ( sys.argv[1:] )

    Retorno:
        parser.Namespace : Una especie de objeto que contiene las propiedades obtenidas
    """

    parser = argparse.ArgumentParser(
        prog=f"{__file__}",
        description=f"Check the state of a ISV server on rlm license server. Ver: {VERSION}",
        epilog="2024(JRM - UAB - SID SBD)"
    )
    parser.add_argument('-H', action="store", required=True, dest="server"  , help="Server Name or IP" )
    parser.add_argument('-P', action="store", required=True, dest="port"    , help="Port of service")
    parser.add_argument('-i', action="store", required=True, dest="isv"     , help="ISV name")
    parser.add_argument('-l', action="store", required=True, dest="num_lic" , type=int, help="Number of licences.")
    parser.add_argument('-w', action="store", required=True, dest="warn_lic", type=int, help="Number of licences used for warning.")
    parser.add_argument('-c', action="store", required=True, dest="crit_lic", type=int, help="Number of licences used for critical.")
    parser.add_argument('-W', action="store", required=True, dest="warn_expiration", type=int, help="Days to expiration for warning.")
    parser.add_argument('-C', action="store", required=True, dest="crit_expiration", type=int, help="Days to expiration for critical.")
    parser.add_argument('-p', action="store", required=False, dest="rlmutil", help="rlmutil path.", default="rlmutil")

    xx = parser.parse_args() 

    log.debug( f"Arguments : {xx}" )

    log.debug( f" num_lic: {xx.num_lic}")

    if( xx.warn_lic >  xx.num_lic ):
        log.critical( f"Error: warn_lic {xx.warn_lic} > num_lic {xx.num_lic} ")
        parser.print_help(sys.stderr)
        sys.exit (NAGIOS_UNKNOWN)
    #
    if( xx.crit_lic >  xx.num_lic ):
        log.critical( f"Error: crit_lic > num_lic ")
        parser.print_help(sys.stderr)
        sys.exit (NAGIOS_UNKNOWN)
    #

    if( xx.warn_lic >  xx.crit_lic ):
        log.critical( f"Error: warn_lic > crit_lic ")
        parser.print_help(sys.stderr)
        sys.exit (NAGIOS_UNKNOWN)
    #

    if( xx.warn_expiration <  xx.crit_expiration ):
        log.critical( f"Error: warn_expiration > crit_expiration ")
        parser.print_help(sys.stderr)
        sys.exit (NAGIOS_UNKNOWN)
    #

    return xx    
#


#
# main code
if __name__ == "__main__":
    LOGLEVEL = os.environ.get('LOGLEVEL','INFO')
    logging.basicConfig( stream=sys.stdout, level=LOGLEVEL ) 
    
    log = logging.getLogger( __name__ )


    opciones = parse_args (sys.argv[1:]) 
    log.debug( f"Opciones: {opciones}" )
    log.debug( f"Server : {opciones.server}" )

    # Lanzamos el comando
    if ( shutil.which(opciones.rlmutil) is None ):
        log.critical("rlmutil not found.")
        sys.exit ( NAGIOS_UNKNOWN )
    #

    comando = [ opciones.rlmutil, 
                'rlmstat', 
                '-c', 
                opciones.port+'@'+opciones.server, 
                '-a',
                '-i',
                opciones.isv
                ]

    log.debug( f"Comando : {comando} - '{ ' '.join( comando ) }'." )

    # Ejecuta el comando y capturamos la salida
    proceso = subprocess.Popen(comando, stdout=subprocess.PIPE)
    salida, _ = proceso.communicate()
    codigo_retorno = proceso.returncode

    resultado = salida.decode('utf-8')

    log.debug( f"Errorlevel: {codigo_retorno}")
    log.debug( f"stdout:\n{resultado}\nEOT")

    if ( codigo_retorno != 0 ):

        error_regexp = r'^(?P<error_info>.*(Error|\([0-9]\)).*)$'

        coincidencias = re.finditer(error_regexp, resultado, re.MULTILINE)

        # Mostrar los grupos con nombre
        for coincidencia in coincidencias:
            
            log.info( f"{coincidencia.group('error_info')}")
        #
        sys.exit( NAGIOS_CRIT )
    #
        
    softwareRegExp = r"^\s+-+\n\s+(?P<isv>.*) license pool status on (?P<server>.*) \(port (?P<port>[0-9]+)\)\s+(?P<software>.+), pool: (?P<pool>[0-9]+)\n\s+count:.(?P<count>[0-9]+).+reservations: (?P<reservations>[0-9]+).+inuse: (?P<inuse>[0-9]+).+exp: (?P<expire>(..)-(...)-(....))"

    coincidencias = re.finditer(softwareRegExp, resultado, re.MULTILINE)

    info = {}
    num_coincidencia=0
    for coincidencia in coincidencias:

        info['isv']              = coincidencia.group('isv')
        info['server']           = coincidencia.group('server')
        info['port']             = coincidencia.group('port')
        info['soft']             = coincidencia.group('software')
        info['pool']             = coincidencia.group('pool')
        info['count']            = int(coincidencia.group('count'))
        info['reservations']     = int(coincidencia.group('reservations'))
        info['inuse']            = int(coincidencia.group('inuse'))
        info['expire']           = datetime.strptime( coincidencia.group('expire'), "%d-%b-%Y" )
        num_coincidencia += 1 

    #
    log.debug( f"Coincidencias {num_coincidencia} ->  {info}.")

    if ( num_coincidencia != 1 ):

        log.info (f"ERROR. License info NOT FOUND. check with '{' '.join( comando ) }'")
        sys.exit (NAGIOS_CRIT)
    #

    NAGIOS_RETURN = NAGIOS_UNKNOWN
    NAGIOS_PREFIX = "UNKNOWN"

    # Calculamos dias entre caducidad y hoy
    fecha_actual  = datetime.now()
    dias = (info['expire'] - fecha_actual).days    


    if( info['inuse'] < (info['count'] + info['reservations'] ) ):
        NAGIOS_RETURN = NAGIOS_OK
        NAGIOS_PREFIX = "OK"
    #
    if( info['inuse'] >= opciones.warn_lic ):
        NAGIOS_RETURN = NAGIOS_WARN
        NAGIOS_PREFIX = "WARNING IN USE"
    #

    if( dias <= opciones.warn_expiration ):
        NAGIOS_RETURN = NAGIOS_WARN
        NAGIOS_PREFIX = "WARNING EXPIRATION"
    #

    if( info['inuse'] >= opciones.crit_lic ):
        NAGIOS_RETURN = NAGIOS_CRIT
        NAGIOS_PREFIX = "CRITICAL IN USE"
    #

    if( dias <= opciones.crit_expiration ):
        NAGIOS_RETURN = NAGIOS_CRIT
        NAGIOS_PREFIX = "CRITICAL EXPIRATION"
    #

    if( info['count'] != opciones.num_lic ):
        NAGIOS_RETURN = NAGIOS_CRIT
        NAGIOS_PREFIX = "CRITICAL LICENSE NUMBER"

    print( f"{NAGIOS_PREFIX}: RLM {info['server']}:{info['port']} - '{info['isv']}' [{info['soft']}] : {info['inuse']}/{info['count']}+{info['reservations']} until {info['expire']} ([{dias} days])")


    sys.exit( NAGIOS_RETURN)
#