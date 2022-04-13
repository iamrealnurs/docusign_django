from asyncio.log import logger
from importlib.resources import contents
from unittest import result
from urllib import response
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import base64
import requests
import os
from docusign_esign import RecipientViewRequest, EnvelopeDefinition, Document, Signer, SignHere, Tabs, Recipients, ApiClient, EnvelopesApi, Text, DateSigned, CarbonCopy
from django.views.decorators.csrf import csrf_exempt
import json
import jwt
from .tokens import docusign_token
from datetime import date
from rest_framework.decorators import api_view
from rest_framework import status
from pprint import pprint


CLIENT_AUTH_ID = settings.CLIENT_AUTH_ID
BASE_DIR = settings.BASE_DIR
CLIENT_USER_ID = settings.CLIENT_USER_ID
ACCOUNT_ID = settings.ACCOUNT_ID

def create_jwt_grant_token():
    print('*****begin create_jwt_grant_token*****')
    print('--------------------------------')
    token = docusign_token()
    print('token')
    print(token)
    print('--------------------------------')
    logger.info('TOKEN', token)
    print('*****end create_jwt_grant_token*****')
    return token

def signature_by_email(token, base64_file_content, signer_name, signer_email):
    try:
        # Создание документа
        document = Document(# Create the docusign document object
            document_base64 = base64_file_content,
            name = 'Example document',
            file_extension = 'pdf',
            document_id = '1'
        )
        sign_here = SignHere(
            document_id = '1',
            page_number = '1',
            recipient_id = '1',
            tab_label = 'SignHereTab',
            y_position = '513',
            x_position = '80'
        )
        today = date.today()
        curr_date = today.strftime('%d/%m/%Y')
        sign_date = DateSigned(
            document_id = '1',
            page_number = '1',
            recipient_id = '1',
            tab_label = 'Date',
            font = 'helvetica',
            bold = 'true',
            value = curr_date,
            tab_id = 'date',
            font_size = 'size16',
            y_position='55',
            x_position='650'
        )
        text_name = Text(
            document_id = '1',
            page_number = '1',
            recipient_id = '1',
            tab_label = 'Name',
            font='helvetica',
            bold = 'true',
            value = signer_name,
            tab_id='name',
            font_size='size16',
            y_position='304',
            x_position='82'
        )
        text_email = Text(
            document_id = '1',
            page_number = '1',
            recipient_id = '1',
            tab_label = 'Email',
            font='helvetica',
            bold = 'true',
            value = signer_email,
            tab_id='email',
            font_size='size16',
            y_position='304',
            x_position='82'
        )

        signer_tab = Tabs(sign_here_tabs=[sign_here], text_tabs=[text_name, text_email, sign_date])
        signer = Signer(
            email=signer_email, name=signer_name, recipient_id='1', routing_order='1', tabs=signer_tab
        )
        #Делаем сс копию документа
        cc1 = CarbonCopy(
            email=signer_email,
            name = signer_name,
            recipient_id = '2',
            routing_order = '2'
        )

        envelope_definition = EnvelopeDefinition(
            email_subject='Please sign this document sent from the python sdk',
            documents = [document],
            recipients = Recipients(signers = [signer], carbon_copies = cc1),
            status = 'sent'
        )
        try:
            api_client = ApiClient()
            api_client.host = 'https://demo.docusign.net/restapi'
            api_client.set_default_header('Authorization', 'Bearer' + token['access_token'])

            envelope_api = EnvelopesApi(api_client)
            results = envelope_api.create_envelope(ACCOUNT_ID=ACCOUNT_ID, envelope_definition=envelope_definition)
            envelope_id = results.envelope_id
            return envelope_id
        except Exception as e:
            return JsonResponse({
                'docusign_url': '',
                'envelope_id': '',
                'message': 'Internal Server Error',
                'error': 'in signature by email: '+str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JsonResponse({
                'docusign_url': '',
                'envelope_id': '',
                'message': 'Internal Server Error',
                'error': 'in signature by email: '+str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def signature_by_embedded(token, base64_file_content, signer_name, signer_email):
    try:
        document = Document(# Create the docusign document object
            document_base64 = base64_file_content,
            name = 'Example document',
            file_extension = 'pdf',
            document_id = '1'
        )
        sign_here = SignHere(
            document_id = '1',
            page_number = '1',
            recipient_id = '1',
            tab_label = 'SignHereTab',
            y_position = '513',
            x_position = '80'
        )
        today = date.today()
        curr_date = today.strftime('%d/%m/%Y')
        sign_date = DateSigned(
            document_id = '1',
            page_number = '1',
            recipient_id = '1',
            tab_label = 'Date',
            font = 'helvetica',
            bold = 'true',
            value = curr_date,
            tab_id = 'date',
            font_size = 'size16',
            y_position='55',
            x_position='650'
        )
        text_name = Text(
            document_id = '1',
            page_number = '1',
            recipient_id = '1',
            tab_label = 'Name',
            font='helvetica',
            bold = 'true',
            value = signer_name,
            tab_id='name',
            font_size='size16',
            y_position='304',
            x_position='82'
        )
        text_email = Text(
            document_id = '1',
            page_number = '1',
            recipient_id = '1',
            tab_label = 'Email',
            font='helvetica',
            bold = 'true',
            value = signer_email,
            tab_id='email',
            font_size='size16',
            y_position='304',
            x_position='82'
        )
        
        signer_tab = Tabs(sign_here_tabs=[sign_here], text_tabs=[text_name, text_email, sign_date])
        signer = Signer(
            email = signer_email, name = signer_name, recipient_id = '1', routing_order = '1', CLIENT_USER_ID = 'CLIENT_USER_ID', tabs = signer_tab
        )

        envelope_definition = EnvelopeDefinition(
            email_subject='Please sign this document sent from the python sdk',
            documents = [document],
            recipients = Recipients(signers = [signer]),
            status = 'sent'
        )
        
        api_client = ApiClient()
        api_client.host = 'https://demo.docusign.net/restapi'
        api_client.set_default_header('Authorization', 'Bearer' + token['access_token'])

        envelope_api = EnvelopesApi(api_client)
        results = envelope_api.create_envelope(ACCOUNT_ID=ACCOUNT_ID, envelope_definition=envelope_definition)
        envelope_id = results.envelope_id
        envelope_status = results.envelope_status
        recipient_view_request = RecipientViewRequest(
            authentication_method='email',
            CLIENT_USER_ID = CLIENT_USER_ID,
            recipient_id = '1',
            return_url = 'https://127.0.0.1:8000/sign_completed',
            user_name = signer_name,
            email = signer_email
        )
        results = envelope_api.create_recipient_view(ACCOUNT_ID, envelope_id, recipient_view_request = recipient_view_request)
        return results.url
    except Exception as e:
        return JsonResponse({
            'docusign_url':'',
            'message': 'Internal server error',
            'error': 'In Signature by emdedded: '+str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def docusign_signature(request):
    try:
        print('--------------------------------')
        token = create_jwt_grant_token()
        print('--------------------------------')
        print('token')
        print(token)
        print('--------------------------------')
        post_data = {'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer', 'assertion': token}
        base_url = 'https://account-d.docusign.com/oauth/token'
        r = requests.post(base_url, data=post_data)
        token = r.json()
        data = json.loads(request.body)
        print('********************************')
        pprint(data.__dict__)
        print('********************************')
        signer_email = data['email']
        signer_name = data['full_name']
        signer_type = data['type']
        # Находим документ который надо подписать
        with open(os.path.join(BASE_DIR, '/core/docusign_files/' 'b.pdf'), 'rb') as file: #нужный документ
            content_bytes = file.read()
        base64_file_content = base64.b64encode(content_bytes).decode('ascii')

        if signer_type == 'embedded':
            url, envelope_id = signature_by_embedded(token, base64_file_content, signer_name, signer_email)
        if signer_type == 'email':
            envelope_id = signature_by_email(token, base64_file_content, signer_name, signer_email)
            url = ''
        return JsonResponse({
            'docusign_url': url,
            'envelope_id': envelope_id,
            'message': 'Docusign',
            'error': ''
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({
            'docusign_url': '',
            'envelope_id': '',
            'message': 'Internal Server Error1',
            'error': 'In docusign signature: '+str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def sign_completed(request):
    return HttpResponse('Signing completed successfully')

@api_view(['GET'])
@csrf_exempt
def get_envelope_status(request, envelope_id):
    token = create_jwt_grant_token()
    post_data = {'grant_type':'urn:ietf:params:oauth:grant-type:jwt-bearer', 'assertion':token}
    base_url = 'https://account-d.docusign.com/oauth/token'
    r = requests.post(base_url, data=post_data)
    token = r.json()
    base_url = 'https://demo.docusign.net/restapi/v2.1/accounts/{0}/envelopes/{1}'.format(ACCOUNT_ID, envelope_id)
    r = requests.get(base_url, headers={
        'Authorization': 'Bearer '+ token['access_token']})
    response = r.json()
    logger.info('response: %s', response)
    return JsonResponse({
        'response': response,
        'error': ''
    }, status=status.HTTP_200_OK)
