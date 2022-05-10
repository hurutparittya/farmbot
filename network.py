from crypto import decrypt, encrypt
import requests
import json
import logging

class Network():
    XER = "unity_beta"
    HEADER = {
                "Host":"www.farmerama.com",
                "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0",
                "Accept":"*/*",
                "Accept-Language":"en-US,en;q=0.5",
                "Accept-Encoding":"gzip, deflate, br",
                "Content-Type":"application/x-www-form-urlencoded",
                "Origin":"https://www.farmerama.com",
                "Connection":"keep-alive",
                "Referer":"https://www.farmerama.com/?action=internalGameUnity",
                "TE":"Trailers"}
    APIURL = "https://www.farmerama.com/FarmAPI.php"
    
    def __init__(self,session):
        self.logger = logging.getLogger("network")
        self.session = session       
        self.token = 0
        self.token = self.makeRequest("config.gC",{"config.gC":{"bw":-1}})["cCfg"]["token"]
        self.logger.info("initialized token as " + self.token)

    def makeRequest(self,req,jsonDict):
        jsonString = json.dumps(jsonDict)
        params = {
                "uId":self.session.uid,
                "tok":self.token,
                "xer":self.XER,
                "req":req}
        data = {
                "tok":self.token,
                "uId":self.session.uid,
                "base64":encrypt(jsonString)}

        response = requests.post(self.APIURL,headers=self.HEADER,data=data,params=params,cookies=self.session.cookies)
        responseString = decrypt(response.text)
        jsonResponse = json.loads(responseString)
        if "err" in jsonResponse or "noAuthUser" in jsonResponse:
            self.logger.error("request: " + jsonString)
            self.logger.error("response: " + responseString)
            raise Exception("network error")
        return jsonResponse

