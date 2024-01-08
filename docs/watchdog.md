Introduction
------------
## About Watchdog

Watchdog serves as a sophisticated licensing server meticulously crafted to elevate the license verification process for
BrowserMon. Engineered with precision, it stands as a cornerstone in license management, ensuring the integrity and
security of controllers' licenses.
Features

- **License Verification:** Watchdog boasts a robust API dedicated to validating the authenticity of controllers'
  licenses. This ensures a secure and authenticated gateway to access essential services.

- **Active GUIDs Retrieval:** The server not only verifies licenses but also offers a comprehensive feature for
  retrieving active GUIDs. This functionality provides valuable insights into the current roster of registered
  controllers, contributing to effective monitoring and management.

Watchdog goes beyond a mere licensing tool; it is a cornerstone in the reliability and security of BrowserMon's
operational infrastructure.


Getting Started
---------------
If you're new to Watchdog, follow these steps to quickly get started:

1. **Download Binaries:** Obtain the binaries for your operating system from the [
   *releases*](https://github.com/eunomatix/watchdog/releases).

2. **Extract and Configure:** Extract the downloaded zip file. Add your provided *BMKEY* and *AUTHCODE* to the
   configuration file.

3. **Run the Server:** Execute the binary to start Watchdog.

```bash
./Watchdog --config-path /path/to/watchdog.conf
```

4. To generate the SSL certificate run the following command. You can change your cert config in the `ssl_config.ini` file.
```bash
./Watchdog --config-path /path/to/watchdog.conf --generate-ssl
```

Watchdog Installation
---------------------
To seamlessly integrate Watchdog into your system, follow these straightforward steps:

1. Download the latest Watchdog binaries for the Linux from
   the [Watchdog Releases](https://github.com/eunomatix/watchdog/releases).
2. Extract the downloaded zip file to unveil the essential components.
3. Ensure the `watchdog.conf` file is passed as the arg to the Watchdog.
4. Populate your `watchdog.conf` file with the provided *BMKEY* and *AUTHCODE*.
5. Ready to roll! Execute the binary using the following command:

```bash
./Watchdog --config-path /path/to/watchdog.conf
```

6. To generate the SSL certificate run the following command. You can change your cert config in the `ssl_config.ini`
   file.

```bash
./Watchdog --config-path /path/to/watchdog.conf --generate-ssl
```

Experience the power of Watchdog as it efficiently manages and verifies licenses for enhanced security and operational
control.
For the latest releases, explore the Watchdog [releases page](https://github.com/eunomatix/watchdog/releases).


Configuration
-------------

Watchdog relies on the watchdog.conf configuration file for essential settings. Here are the key configuration
parameters:

- `MODE:` Set the mode to either 'local' or 'cloud' based on your deployment.
- `BMKEY:` Provide the Base64-encoded license key.
- `AUTHCODE:` Add the Base64-encoded authorization code.
- `BLACKLIST:` Specify the blacklist configuration.
- `LOGDIR`: Path to your log directory.
- `LOGLEVEL`: Set the desired loglevel. Set it to `DEBUG` if the program doesn't work the intended way.
- `LIMIT`: Enable the rate limiting.
- `RATE`: Give the rate on which API is accessible.

- `CERTFILE`: Path to the SSL Certificate File
- `KEYFILE`: Path to the SSL Key File

Api Reference
-------------
### Check License

The `check-license` API endpoint is designed to verify the validity of controllers' licenses.

**Endpoint:** `POST /api/check-license/`

**Parameters:**

- `guid` (UUID v1) - **Required.** Controller Guid.
- `hostname` (String) - **Required** System Hostname
- `version` (String) - **Required** Controller Version
- `ip_addresses` (List) - **Required** List of Controller IPs

### Get Active GUIDs

The `get-licenses` API endpoint retrieves the list of active GUIDs.

**Endpoint:** `GET /api/get-licenses/`

**Description:**
Display the list of active licensed controllers.