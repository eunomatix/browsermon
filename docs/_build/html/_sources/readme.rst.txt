.. role:: raw-latex(raw)
   :format: latex
..

|BrowserMon|

|Static Badge| |image1|

BrowserMon - Revolutionary Browser Monitoring Tool
==================================================

Welcome to Browsermon, the revolutionary browser monitoring tool
designed to provide unparalleled insights into browsing activities. With
seamless compatibility with Google Chrome , Mozilla Firefox and Microsoft Edge browsers, Browsermon stands
as a unique solution in the realm of browser monitoring. Whether
operating in real-time mode or scheduled mode, this tool meticulously
records browsing histories, capturing a comprehensive range of 17
distinct parameters.

.. Features
.. --------

.. -  **Comprehensive Monitoring**: BrowserMon captures a rich set of 17
..    browsing parameters, providing a comprehensive view of browsing
..    activities. This depth of data enables accurate analysis and informed
..    decision-making.

.. -  **Data Privacy**: BrowserMon focuses solely on browser history and
..    does not infringe upon broader internet activity or compromise user
..    privacy beyond the scope of browsing data.

.. -  **Non-Intrusive Monitoring**: One of the standout benefits of
..    BrowserMon is its non-intrusive monitoring capability. Regardless of
..    the operating system you’re using, BrowserMon operates seamlessly
..    behind the scenes without causing disruptions or interfering with
..    other data on your system. 

.. -  **Centralized management with Watchdog -Only for enterprise version :**: Browsermon enterprise is managed 
..    by Watchdog.Which serves as a centralized management and licensing server for Browsermon 
..    agents installed in the enterprise. Watchdog operates on a dedicated Linux server (or VM) 
..    and registers all enterprise Browsermon instances to perform health checking and
..    validate licenses.
   


Browsermon application caputres a rich set of 17 browsing parameters
in **CSV** or **JSON** format.

.. list-table::
   :widths: 25 75

   * - :Parameter:  
     - :Description: 
   * - hostname
     - The name of the host computer.
   * - os
     - Operating system used (e.g., Windows).
   * - os_username
     - Operating system username.  
   * - browser
     - Web browser used (e.g., edge).
   * - browser_version
     - Version of the web browser.  
   * - browser_db
     - Database type/version used by the browser.  
   * - profile_id
     - Identifier for the browser profile (if applicable)..  
   * - profile_title
     - Title of the browser profile..  
   * - profile_username
     - Username associated with the browser profile..  
   * - profile_path
     - File path to the browser profile data.  
   * - username
     - Username of the profile..  
   * - session_id
     - Unique identifier for the session.  
   * - referrer
     - Referrer URL (if any). 
   * - url
     - URL of the webpage visited.  
   * - title
     - Title of the webpage visited.  
   * - visit_time
     - Time of the visit..  
   * - visit_count
     - Number of times the URL was visited.


.. License
.. -------

.. Browsermon Comm is available under MIT License


.. MIT License

.. Copyright (c) 2023 Eunomatix

.. Permission is hereby granted, free of charge, to any person obtaining a
.. copy of this software and associated documentation files (the
.. “Software”), to deal in the Software without restriction, including
.. without limitation the rights to use, copy, modify, merge, publish,
.. distribute, sub-license, and/or sell copies of the Software, and to
.. permit persons to whom the Software is furnished to do so, subject to
.. the following conditions:

.. The above copyright notice and this permission notice shall be included
.. in all copies or substantial portions of the Software.

.. \**THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
.. EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
.. MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
.. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
.. CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
.. TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
.. SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

.. |BrowserMon| image:: https://browsermon.ai/wp-content/uploads/2023/08/BrowserMon-Logo.png
   :target: https://github.com/eunomatix/browsermon
.. |Static Badge| image:: https://img.shields.io/badge/Version-1.2.1--alpha-brightgreen
.. |image1| image:: https://img.shields.io/badge/License-MIT-blue

.. Browsermon Community Version Installation
.. =========================================
 
.. To build the project:

.. 1. Get the source code:
..    ``git clone https://github.com/eunomatix/browsermon``

.. 2. Create a Python environment: ``python -m venv venv`` Install
..    dependencies in the environment: ``pip install -r requirements.txt``
..    **Note**: For Windows, you will also have to install *pywin32*, which
..    is not present in the requirement.txt file: ``pip install pywin32``

.. 3. Create executable using PyInstaller:
..    ``pyinstaller -F src/browsermon.py`` For Windows:
..    ``pyinstaller --hiddenimport win32timezone -F src/browsermon.py``

.. 4. Run service install scripts: ``./linux_install.sh`` or
..    ``Set-ExecutionPolicy RemoteSigned -Force ; .\win_install.ps1``

.. Browsermon Enterprise Version Installation
.. ==========================================

.. **Windows**
.. To install, download the browsermon.zip file, extract the file and
.. open powershell as administrator where you extracted the file. Run
.. the following command
..    ``Set-ExecutionPolicy RemoteSigned -Force ; .\win_install.ps1`` 
.. **Linux**
.. Download the ``browsermon_linux-x64.zip`` extract it and run
.. ``linux_install.sh`` as sudo ## Watchdog Installation #### Linux Only
.. To seamlessly integrate Watchdog into your system, follow these
.. straightforward steps:

.. 1. Download the latest Watchdog binaries for the Linux 
.. 2. Extract the downloaded zip file to unveil the essential components.
.. 3. Ensure the ``watchdog.conf`` file is passed as the arg to the
..    Watchdog.
.. 4. Populate your ``watchdog.conf`` file with the provided *BMKEY* and
..    *AUTHCODE*.
.. 5. Ready to roll! Execute the binary using the following command:

.. .. code:: bash

..    ./Watchdog --config-path /path/to/watchdog.conf

.. 6. To generate the SSL certificate run the following command. You can
..    change your cert config in the ``ssl_config.ini`` file.

.. .. code:: bash

..    ./Watchdog --config-path /path/to/watchdog.conf --generate-ssl

.. Experience the power of Watchdog as it efficiently manages and verifies
.. licenses for enhanced security and operational control. For the latest
.. releases, explore the Watchdog `releases
.. page <https://github.com/eunomatix/watchdog/releases>`__.


