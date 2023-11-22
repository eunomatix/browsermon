[![BrowserMon][repo_logo_img]][repo_url]

![Static Badge](https://img.shields.io/badge/Version-1.2.1--alpha-brightgreen)
![Static Badge](https://img.shields.io/badge/License-MIT-blue)

# BrowserMon - Revolutionary Browser Monitoring Tool

Welcome to BrowserMon, the revolutionary browser monitoring tool designed to provide unparalleled insights into browsing activities. With seamless compatibility with Chrome and Edge browsers, BrowserMon stands as a unique solution in the realm of browser monitoring. Whether operating in real-time mode or scheduled mode, this tool meticulously records browsing histories, capturing a comprehensive range of 17 distinct parameters.

## Features

- **Comprehensive Monitoring**: BrowserMon captures a rich set of 17 browsing parameters, providing a comprehensive view of browsing activities. This depth of data enables accurate analysis and informed decision-making.

- **Data Privacy**: BrowserMon focuses solely on browser history and does not infringe upon broader internet activity or compromise user privacy beyond the scope of browsing data.

- **Non-Intrusive Monitoring**: One of the standout benefits of BrowserMon is its non-intrusive monitoring capability. Regardless of the operating system you’re using, BrowserMon operates seamlessly behind the scenes without causing disruptions or interfering with other data on your system.
# BrowserMon Application
BrowserMon application caputres a rich set of 17 browsing parameters in **CSV** or **JSON** format. 
| Parameter         | Description                                        |
|-------------------|----------------------------------------------------|
| `hostname`        | The name of the host computer.                     |
| `os`              | Operating system used (e.g., Windows).             |
| `os_username`     | Operating system username.                         |
| `browser`         | Web browser used (e.g., edge).                     |
| `browser_version` | Version of the web browser.                        |
| `browser_db`      | Database type/version used by the browser.         |
| `profile_id`      | Identifier for the browser profile (if applicable).|
| `profile_title`   | Title of the browser profile.                      |
| `profile_username`| Username associated with the browser profile.      |
| `profile_path`    | File path to the browser profile data.             |
| `username`        | Username of the profile.                           |
| `session_id`      | Unique identifier for the session.                 |
| `referrer`        | Referrer URL (if any).                             |
| `url`             | URL of the webpage visited.                        |
| `title`           | Title of the webpage visited.                      |
| `visit_time`      | Time of the visit.                                 |
| `visit_count`     | Number of times the URL was visited.               |

![json-showcase](/images/browsingParams.png)

browserMon Application supports Windows and Linux, for installing refer [Installation](#installation)
<br>
![windows-logo][windows-logo]
![Linux-logo][linux-logo]
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
## Troubleshooting
[Troubelshooting guide](docs/Troubeshoot.md)

## License

[MIT License](/LICENSE)

[repo_logo_img]: https://browsermon.ai/wp-content/uploads/2023/08/BrowserMon-Logo.png
[repo_url]: https://github.com/eunomatix/browsermon
[linux-logo]: https://browsermon.ai/wp-content/uploads/2023/08/Linux.png
[windows-logo]: https://browsermon.ai/wp-content/uploads/2023/08/Windows-11.png