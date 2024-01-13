
Community Version
=================

In the community version of Browsermon, users have access to a limited set of
features that cater to essential browser monitoring needs. This version includes
specialized functionalities such as the Google Chrome Reader, Mozilla Firefox Reader,
and Microsoft Edge Reader. These features empower users to monitor and analyze browsing 
activities on these popular web browsers, providing valuable insights into user behavior 
and potential security threats.

It's important to note that while the community version offers a range of capabilities, 
it operates under certain limitations, including running on a single device. 
This constraint aligns with the community-oriented nature of the version, making it suitable 
for individual users  seeking basic browser monitoring functionalities. The availability of 
these features in the community version allows users to experience the benefits of Browsermon's
capabilities while also providing an opportunity for broader adoption within various user communities.

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


Browsermon community version  installtaion
------------------------------------------
Browsermon Community version can run as standalone agent in any Windows or Linux machine as a service.
You can install and build the Browsermon Community version in below simple steps:



1. Get the source code:
   ``git clone https://github.com/eunomatix/browsermon``

2. Create a Python environment: ``python -m venv venv`` Install
   dependencies in the environment: ``pip install -r requirements.txt``
   
   **Note**: For Windows, you will also have to install *pywin32*, which
   is not present in the requirement.txt file: ``pip install pywin32``

3. Create executable using PyInstaller:
  
   For Linux: ``pyinstaller -F src/browsermon.py`` 
   
   For Windows: ``pyinstaller --hiddenimport win32timezone -F src/browsermon.py``

4. Run service install scripts: ``./linux_install.sh`` or
   ``Set-ExecutionPolicy RemoteSigned -Force ; .\win_install.ps1``

Lisence 
-------

Browsermon Community is available under MIT License


MIT License

Copyright (c) 2023 Eunomatix

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
“Software”), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sub-license, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

\**THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
