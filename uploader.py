import requests
import webbrowser
import configparser
import base64
import progressbar
import sys
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

AUTHORIZATION_URL = "https://api.imgur.com/oauth2/authorize"
TOKEN_URL = "https://api.imgur.com/oauth2/token"
RESPONSE_TYPE = "token"

class ImgurAuthorizer:

    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__config.read('.client_secrets')

    def authorizeClient(self):
        url = AUTHORIZATION_URL + "?client_id=%s&response_type=%s" % (self.__config['credentials']['client_id'], RESPONSE_TYPE)
        webbrowser.open(url)

    def getNewRefreshToken(self):
        url = TOKEN_URL
        payload = {
            'refresh_token': self.__config['credentials']['refresh_token'],
            'client_id': self.__config['credentials']['client_id'],
            'client_secret': self.__config['credentials']['client_secret'],
            'grant_type': 'refresh_token'
        }

        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(response.json())
            print("Error getting new access token.")
            return None
        else:
            self.__config['credentials']['access_token'] = response.json()['access_token']
            self.__config.write()

        return response.json()['access_token']

    def isAuthorized(self):
        return self.__config['credentials']['access_token'] != ""

    def updateTokens(self, access_token, refresh_token):
        self.__config['credentials']['access_token'] = access_token
        self.__config['credentials']['refresh_token'] = refresh_token
        self.__config.write()

    def getAccessToken(self):
        return self.__config['credentials']['access_token']


class ImgurUploader:

    def __init__(self):
        self.__bar = None

    def __create_callback(self, encoder, filename):
        widgets = [' ', progressbar.Percentage(),  ' ', progressbar.SimpleProgress()]
        self.__bar = progressbar.ProgressBar(widgets=widgets, max_value=encoder.len, prefix="Uploading " + filename).start()

        def callback(monitor):
            self.__bar.update(monitor.bytes_read)

        return callback

    def __finishUpload(self):
        self.__bar.finish()

    def __buildHeaders(self, access_token, content_type):
        headers = {
            'Authorization': 'Bearer %s' % access_token,
            'Content-Type': content_type
        }
        return headers

    def uploadImage(self, imgurAuthorizer, image_path):
        url = "https://api.imgur.com/3/image"

        with open(image_path, 'rb') as image_file:
            contents = image_file.read()
            b64_image = base64.b64encode(contents)
            payload = {
                'image': b64_image,
                'type': 'base64',
            }

            encoder = MultipartEncoder(fields=payload)
            callback = self.__create_callback(encoder, image_path)
            monitor = MultipartEncoderMonitor(encoder, callback=callback)

            headers = self.__buildHeaders(imgurAuthorizer.getAccessToken(), monitor.content_type)
            response = requests.post(url, headers=headers, data=monitor, files=[])
            if response.status_code == 403:
                new_access_token = imgurAuthorizer.getNewAccessToken()
                if new_access_token == None:
                    return
                headers = self.__buildHeaders(new_access_token, monitor.content_type)
                response = requests.post(url, headers=headers, data=monitor, files=[])

            self.__finishUpload()

            return response.json()['data']

if __name__ == '__main__':
    imgurAuthorizer = ImgurAuthorizer()

    if not imgurAuthorizer.isAuthorized():
        imgurAuthorizer.authorizeClient()

        access_token = input("Access Token:")
        refresh_token = input("Refresh Token:")

        imgurAuthorizer.updateTokens(access_token, refresh_token)

    if len(sys.argv) > 1:
        imgurUploader = ImgurUploader()
        for image in sys.argv[1:]:
            data = imgurUploader.uploadImage(imgurAuthorizer, image)
            print("Done %s => %s" % (image, data['link']))
