from requests.api import request
import requests
import datetime as dt
import base64
from requests.auth import HTTPBasicAuth

def mpesa_stk(amount, phone_number,mpesa_express_shortcode , mpesa_passkey, mpesa_consumer_key, mpesa_consumer_secret):
    #mpesa code for stkpush
    timestamp=dt.datetime.now().strftime("%Y%m%d%H%M%S")#get timestamp in fom of string

    #get password
    data_to_encode=mpesa_express_shortcode +mpesa_passkey+ timestamp
    encoded=base64.b64encode(data_to_encode.encode())
    decoded_password=encoded.decode('utf-8')

    #auth credentials ur to get an access token
    auth_url ="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    r=requests.get(auth_url, auth=HTTPBasicAuth(mpesa_consumer_key,mpesa_consumer_secret))

    access_token=r.json()['access_token']

    #stk push url
    api_url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers={
        "Authorization":"Bearer %s" % access_token
    }

    

    request_mpesa={
        "BusinessShortCode":mpesa_express_shortcode,    
        "Password": decoded_password,    
        "Timestamp":timestamp,    
        "TransactionType": "CustomerPayBillOnline",    
        "Amount":100,    
        "PartyA":f"{phone_number}",    
        "PartyB":mpesa_express_shortcode,    
        "PhoneNumber":f"{phone_number}",    
        "CallBackURL":"https://8626-102-135-169-126.eu.ngrok.io/api/Likes",    
        "AccountReference":"RESERVESPACE",    
        "TransactionDesc":"Car parking payment"
    }

    response=requests.post(api_url, json=request_mpesa, headers=headers)
    return response