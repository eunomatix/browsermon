Browsermon Enterprise Installation
==================================

Windows
-------

-  To install, download the browsermon.zip file, extract the file and
   open powershell as administrator where you extracted the file. Run
   the following command
   ``Set-ExecutionPolicy RemoteSigned -Force ; .\win_install.ps1`` ####
   Linux
-  Download the ``browsermon_linux-x64.zip`` extract it and run
   ``linux_install.sh`` as sudo ## Watchdog Installation #### Linux Only
   To seamlessly integrate Watchdog into your system, follow these
   straightforward steps:

1. Download the latest Watchdog binaries for the Linux from the
   `Watchdog
   Releases <https://github.com/eunomatix/watchdog/releases>`__.
2. Extract the downloaded zip file to unveil the essential components.
3. Ensure the ``watchdog.conf`` file is passed as the arg to the
   Watchdog.
4. Populate your ``watchdog.conf`` file with the provided *BMKEY* and
   *AUTHCODE*.
5. Ready to roll! Execute the binary using the following command:

.. code:: bash

   ./Watchdog --config-path /path/to/watchdog.conf

6. To generate the SSL certificate run the following command. You can
   change your cert config in the ``ssl_config.ini`` file.

.. code:: bash

   ./Watchdog --config-path /path/to/watchdog.conf --generate-ssl

Experience the power of Watchdog as it efficiently manages and verifies
licenses for enhanced security and operational control. For the latest
releases, explore the Watchdog `releases
page <https://github.com/eunomatix/watchdog/releases>`__.
