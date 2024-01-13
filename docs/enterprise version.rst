Enterprise Version
==================

To meet the demands of larger enterprises with more complex monitoring needs, Browsermon introduces the Enterprise version,
which comes with enhanced capabilities. The Enterprise version not only retains the functionalities of the community version 
but also introduces a game-changing feature: Centralized Management with Watchdog.Centralized Management with Watchdog is exclusive to 
enterprise version.

Browsermon Enterprise is designed for organizations with more extensive infrastructure and monitoring requirements.
The introduction of Watchdog serves as a pivotal enhancement, offering centralized management and licensing capabilities.
Watchdog operates on a dedicated Linux server or virtual machine (VM) and acts as the command center for all Browsermon
agents deployed within the enterprise. Watchdog's primary role involves registering and monitoring all enterprise Browsermon
instances, conducting health checks, and validating licenses.


Features
--------

-  **Comprehensive Monitoring**: BrowserMon captures a rich set of 17
   browsing parameters, providing a comprehensive view of browsing
   activities. This depth of data enables accurate analysis and informed
   decision-making.

-  **Data Privacy**: BrowserMon focuses solely on browser history and
   does not infringe upon broader internet activity or compromise user
   privacy beyond the scope of browsing data.

-  **Non-Intrusive Monitoring**: One of the standout benefits of
   BrowserMon is its non-intrusive monitoring capability. Regardless of
   the operating system you’re using, BrowserMon operates seamlessly
   behind the scenes without causing disruptions or interfering with
   other data on your system. 

-  **Centralized management with Watchdog**: Browsermon enterprise is managed 
   by Watchdog.Which serves as a centralized management and licensing server for Browsermon 
   agents installed in the enterprise. Watchdog operates on a dedicated Linux server (or VM) 
   and registers all enterprise Browsermon instances to perform health checking and
   validate licenses.
   

Watchdog
--------
Watchdog provides centralized monitoring and management for enterprise deployment
.Watchdog Features includes.

-  **Active GUIDs Retrieval:** Wathcdog offers a comprehensive feature for 
   retrieving active GUIDs. This functionality provides valuable insights 
   into the current roster of registered controllers, contributing to 
   effective monitoring and management.

-  **License Verification:** Watchdog boasts a robust API dedicated to
   validating the authenticity of controllers’ licenses. This ensures a
   secure and authenticated gateway to access essential services.


**Getting Started**
~~~~~~~~~~~~~~~~~~~


1. **Download Binaries:** Obtain the binaries for your operating system
   from the
   `releases <https://github.com/eunomatix/watchdog/releases>`__.

2. **Extract and Configure:** Extract the downloaded zip file. Add your
   provided *BMKEY* and *AUTHCODE* to the configuration file.

3. **Run the Server:** Execute the binary to start Watchdog.

.. code:: bash

   ./Watchdog --config-path /path/to/watchdog.conf

4. To generate the SSL certificate run the following command. You can
   change your cert config in the ``ssl_config.ini`` file.

.. code:: bash

   ./Watchdog --config-path /path/to/watchdog.conf --generate-ssl



**Configuration**
~~~~~~~~~~~~~~~~~


Watchdog relies on the watchdog.conf configuration file for essential
settings. Here are the key configuration parameters:

-  ``MODE:`` Set the mode to either ‘local’ or ‘cloud’ based on your
   deployment.

-  ``BMKEY:`` Provide the Base64-encoded license key.

-  ``AUTHCODE:`` Add the Base64-encoded authorization code.

-  ``BLACKLIST:`` Specify the blacklist configuration.

-  ``LOGDIR``: Path to your log directory.

-  ``LOGLEVEL``: Set the desired loglevel. Set it to ``DEBUG`` if the
   program doesn’t work the intended way.

-  ``LIMIT``: Enable the rate limiting.

-  ``RATE``: Give the rate on which API is accessible.

-  ``CERTFILE``: Path to the SSL Certificate File

-  ``KEYFILE``: Path to the SSL Key File




.. **Api Reference**
.. ~~~~~~~~~~~~~~~~~

.. Check License

.. The ``check-license`` API endpoint is designed to verify the validity of
.. controllers’ licenses.

.. **Endpoint:** ``POST /api/check-license/``

.. **Parameters:**

.. -  ``guid`` (UUID v1) - **Required.** Controller Guid.
.. -  ``hostname`` (String) - **Required** System Hostname
.. -  ``version`` (String) - **Required** Controller Version
.. -  ``ip_addresses`` (List) - **Required** List of Controller IPs


**Get Active GUIDs**


The ``get-licenses`` API endpoint retrieves the list of active GUIDs.

**Endpoint:** ``GET /api/get-licenses/``

**Description:** Display the list of active licensed controllers.

Browsermon Enterprise Version  installtaion
-------------------------------------------

Browsermon Enterprise Version runs in client-server model, 
where Browsermon Controller(s) run on all enterprise endpoints
for local browser history log collection. Whereas a central Browsermon 
Watchdog server is installed to perform health checking and distributed
management of all Browsermon controllers installed endpoints.
|image2|

Controller  installtaion
~~~~~~~~~~~~~~~~~~~~~~~~

**Windows:**

To install, download the `browsermon.zip <https://github.com/eunomatix/browsermon-private/releases>`__ file, extract the file and open powershell as 
administrator where you extracted the file.Run the following command

``Set-ExecutionPolicy RemoteSigned -Force ; .\win_install.ps1`` 

**Linux:**

Download the ``browsermon_linux-x64.zip`` extract it and run
``linux_install.sh`` as sudo

**Watchdog Installation** 
~~~~~~~~~~~~~~~~~~~~~~~~~~
Watchdog Server is supported on Linux only. To seamlessly integrate Watchdog into your system, 
follow these straightforward steps:


1. Download the latest Watchdog release for  Linux 
2. Extract the downloaded zip file.
3. Ensure the watchdog.conf file is passed as the arguments to the Watchdog. 
4. Populate your ``watchdog.conf`` file with the provided *BMKEY* and
   *AUTHCODE*. Please see your license file to find the BMKEY and AUTHCODE for your company. 
   You can also drop email to support@browsermon.ai to get this information.
5. Ready to roll! Execute the binary using the following command:

.. code:: bash

   ./Watchdog --config-path /path/to/watchdog.conf

6. Watchdog to Controller communication is encrypted through SSL. We shipped our own certificates with Watchdog. 
   To generate your own SSL certificates, modify the config in ``ssl_config.ini`` and run the
   following command.
   
.. code:: bash

   ./Watchdog --config-path /path/to/watchdog.conf --generate-ssl


.. |image2| image:: https://browsermon.ai/wp-content/uploads/2024/01/pic.png