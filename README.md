# BrowserMon - Simple Python Application

BrowserMon is a straightforward Python application that monitors web browsers. To run this application, follow the instructions below:

## Prerequisites

- Python 3.x installed on your system.
- Install the required packages using pip:
    ```
    pip install apscheduler
    pip install orjson
    ```

## Setup

1. Clone or download the BrowserMon repository from GitHub.
    
2. Navigate to the root folder of the application.
    
3. **Important:** Ensure that the `browsermon.conf` file is properly set up before running the application. This file contains configuration settings, especially the `logdir` directory path.
    

## Running the Application

1. Open your terminal or command prompt.
    
2. Change the working directory to the root folder of the BrowserMon application.
    
3. To start the application, run the following command:
    
    ```
    python main.py
    ```
    
    This command will initiate the BrowserMon application and start monitoring web browsers.
    

## Running Tests

To ensure the functionality of the application, you can run the provided pytest tests:

1. Ensure you are in the root directory of the BrowserMon application.

2. Run the following command to execute the tests:
    
    ```
    pytest
    ```

   For a more detailed view of the test results, you can use the verbose option:

    ```
    pytest -vv
    ```

## Stopping the Application

To stop the BrowserMon application, simply send a keyboard interrupt signal. You can do this by pressing `Ctrl + C` in the terminal or command prompt where the application is running. This will gracefully terminate the controller and all spawned processes.

Please note that you should only terminate the application when necessary, as unexpected terminations might lead to incomplete data or other issues.

That's it! You have successfully set up and run the BrowserMon application to monitor web browsers. If you encounter any problems or have further questions, feel free to reach out for support. Happy monitoring!

