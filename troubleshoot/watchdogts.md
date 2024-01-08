# Troubleshooting

This section provides some troubleshooting tips related to BrowserMon service.

## Initial Checks

1. **Check Port Status**
   If you are experiencing issues with the Watchdog server, the first step is to check the status of the port it is
   supposed to be running on. Follow these steps to troubleshoot:
    - Use netstat to Check Port Status
      ```bash
      netstat -tuln | grep 8900 
      ```
    - Check if Watchdog is listening on the port 8900 and bind to `0.0.0.0`

2. **Logs**

    - Set the `loglevel` to `DEBUG` in conf file.
    - Review the Watchdog logs and the Gunicorn Server logs. Watchdog generates logs in the `logdir` configured in conf
      file:

        - Watchdog Logs
        - Gunicorn Logs

3. **Process Status**

- Check the status of the process if it is running or not.

    - Check if the process is running
      ```bash
      ps aux | grep Watchdog 
      ```
    - Get the details of the process if it's running
      ```bash
      ps -p <pid> -o pid,ppid,cmd,%cpu,%mem,etime
      ```

## Common Issues and Solutions

### Server Not Starting

- Review your Watchdog Config. Ensure that you are using compatible version of Watchdog.
- Review your `license key` and `authcode`.

### Server Not Behaving As Expected

- Review your SSL certificate is valid and not expired.
- Check you are not exceeding the max controllers limit.

## Contacting Support

Download the Watchdog troubleshooter from the website, which will collect all logs and relevant information and save it
into a file named `watchdog_archive.zip`, which you can then transfer to the team that will help you fix the issue.

- Run the script in the same folder as Watchdog binary or else use absolute paths in the config.
- Make sure that your config contains absolute path of log and cert files.
- To run the troubleshooter, run the following command.

```bash
./WatchdogTS /path/to/your/watchdog.conf /path/to/your/Watchdog_binary 
```

### Privacy Disclaimer

Watchdog troubleshooter collects all relevant information that can help debug the issue. For transparency, here is the
list of items BrowserMon troubleshooter will collect:

1. `watchdog_*.log` `watchdog_gunicorn.log`
2. SSL Certificates
3. System Information (i.e., platform, platform version, architecture, IP address, MAC address, processor, and RAM)
4. Process Information
5. Troubleshooter will run `lsof` to fetch real-time event properties related to Watchdog.

For further details, you can take a look at the troubleshooter script on
Eunomatix’s [GitHub](https://www.github.com/eunomatix/watchdog).
