[![BrowserMon][repo_logo_img]][repo_url]

![Static Badge](https://img.shields.io/badge/Version-1.2.0--alpha-brightgreen)
![Static Badge](https://img.shields.io/badge/License-MIT-blue)

# BrowserMon - Revolutionary Browser Monitoring Tool

Welcome to BrowserMon, the revolutionary browser monitoring tool designed to provide unparalleled insights into browsing activities. With seamless compatibility with Chrome and Edge browsers, BrowserMon stands as a unique solution in the realm of browser monitoring. Whether operating in real-time mode or scheduled mode, this tool meticulously records browsing histories, capturing a comprehensive range of 17 distinct parameters.

## Features

- **Comprehensive Monitoring**: BrowserMon captures a rich set of 17 browsing parameters, providing a comprehensive view of browsing activities. This depth of data enables accurate analysis and informed decision-making.

- **Data Privacy**: BrowserMon focuses solely on browser history and does not infringe upon broader internet activity or compromise user privacy beyond the scope of browsing data.

- **Non-Intrusive Monitoring**: One of the standout benefits of BrowserMon is its non-intrusive monitoring capability. Regardless of the operating system you’re using, BrowserMon operates seamlessly behind the scenes without causing disruptions or interfering with other data on your system.

## Get Started

### Installation

To install using freeze executable/binaries, download the .zip file and follow the instructions mentioned in the release for your specific operating system.

To build the project:

1. Get the source code:
    ```
    git clone https://github.com/eunomatix/browsermon
    ```

2. Create a Python environment:
    ```
    python -m venv venv
    ```
    Install dependencies in the environment:
    ```
    pip install -r requirements.txt
    ```
    **Note**: For Windows, you will also have to install *pywin32*, which is not present in the requirement.txt file:
    ```
    pip install pywin32
    ```

3. Create executable using PyInstaller:
    ```
    pyinstaller -F src/browsermon.py
    ```
    For Windows:
    ```
    pyinstaller --hiddenimport win32timezone -F src/browsermon.py
    ```

4. Run service install scripts:
    ```
    ./linux_install.sh
    ```
    or
    ```
    Set-ExecutionPolicy RemoteSigned -Force ; .\win_install.ps1
    ```

## Troubleshooting Guide
If you encounter issues while using browsermon, this troubleshooting guide is here to help you identify and resolve common problems. Follow these steps to diagnose and address problems you may face:

### Check System Requirements
Ensure that your system meets the following requirements:

- Supported operating system (Windows + Linux)
- Administrative privileges
- Supported web browser (refer to the documentation for compatibility)

### Configuration Errors
If you suspect configuration issues:

- Review the configuration file (browsermon.conf) to check for errors or inconsistencies.
- Ensure that the paths to browsermon and other required files are correctly specified in the configuration file.

### Running Troubleshooting Script (Linux Only)
If the above steps didn't work, and you're using Linux, consider running the browsermon troubleshooting script.
## License

MIT License

Copyright (c) 2023 Eunomatix

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sub-license, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[repo_logo_img]: https://browsermon.ai/wp-content/uploads/2023/08/BrowserMon-Logo.png
[repo_url]: https://github.com/eunomatix/browsermon