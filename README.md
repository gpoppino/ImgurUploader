# imgur.com image uploader
## Introduction
This script uploads images from the file system to your account at https://imgur.com. The names of the file images are passed as arguments to the script like this:

`python3 uploader.py *.jpg`
or
`python3 uploader.py img_one.jpg img_two.jpg`

## Configuration
The script needs a configuration file called `.client_secrets` that is stored in the current directory of the script. The contents are:
```txt
[credentials]
client_id = YOUR_CLIENT_ID
client_secret = YOUR_CLIENT_SECRET
access_token = YOUR_ACCESS_TOKEN
refresh_token = YOUR_REFRESH_TOKEN
```
