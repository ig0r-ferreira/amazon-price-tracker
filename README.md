# Amazon Price Alert

This script sends you an email alert if the Amazon product you are interested in has dropped in price compared to the set price. **Be careful not to run it repeatedly in a short amount of time.** This script was created to be used daily from a task scheduler.

## Requirements

Python version 3.10.6 or higher installed.

## How to install

1. Download the project

2. Create an .env file in the root of the project following the example below:
    ```properties
        # ----------------------- SCRAPE SETTINGS ----------------------
        # Note: Change only if necessary
        REQUEST_HEADERS_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        REQUEST_HEADERS_ACCEPT_LANG="en-US, en;q=0.5"
        
        # ----------------------- DESIRED PRODUCT ----------------------
        TARGET_PRODUCT_URL="LINK TO AMAZON PRODUCT"
        TARGET_PRODUCT_PRICE=200

        # ----------------------- EMAIL SETTINGS -----------------------
        SMTP_SERVER_HOST="smtp.gmail.com"
        SMTP_SERVER_PORT=587
        SMTP_SERVER_USERNAME="YOUR GMAIL ADDRESS"
        SMTP_SERVER_PASSWORD="YOUR GMAIL PASSWORD"

        EMAIL_SENDER = "from@example.com"
        # If there is more than one email, separate them with a comma
        EMAIL_RECIPIENTS = "to@example.com"
        # --------------------------------------------------------------
    ```

3. Open the project folder in Command Prompt or Terminal.

4. Create a virtual environment and install the dependencies by running the following commands:
    -  Using `Poetry` (if you already have it installed):
        ```shell
            poetry install      # create a virtual environment and install dependencies
            poetry shell        # enable the environment
        ```

    - Using built-in `venv` module:

        - Linux or Mac
  
        ```bash
            python -m venv venv                 # create a virtual environment
            source venv/bin/activate            # enable the environment            
            pip install -r requirements.txt     # install the dependencies
        ```
        -  Windows (CMD)
  
        ```cmd
            python -m venv venv                 # create a virtual environment
            venv\Scripts\activate.bat           # enable the environment            
            pip install -r requirements.txt     # install the dependencies
        ```
        - Windows (Power Shell)
  
        ```ps
            python -m venv venv                 # create a virtual environment
            venv\Scripts\activate.ps1           # enable the environment            
            pip install -r requirements.txt     # install the dependencies
        ```

## How to run

```shell
    python amazon_price_tracker
```
