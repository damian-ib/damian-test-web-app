#!flask/bin/python
import json
from flask import Flask, Response, request
import optparse
import os
import openai
import logging
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_api_key_from_secrets_manager() -> str:
    secret_name = "openai-api-key"
    region_name = "eu-west-1"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e
    secret = get_secret_value_response['SecretString']
    return secret

application = Flask(__name__)
openai.api_key = get_api_key_from_secrets_manager()

@application.route('/completion', methods=['GET'])
def get_completion():
    prompt = request.args.get('prompt')
    if prompt is None:
        return Response(json.dumps({'error': 'prompt is required'}), mimetype='application/json', status=400)
    logging.info(f'Received completion request with prompt: {prompt}')
    completion = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=250,
        n=1 # Number of completions to generate
    )
    completion_text = completion.choices[0].text
    completion_id = completion.id
    response_data = {
        'id': completion_id,
        'text': completion_text
    }
    return Response(json.dumps(response_data), mimetype='application/json', status=200)

@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

if __name__ == '__main__':
    default_port = "80"
    default_host = "0.0.0.0"
    parser = optparse.OptionParser()
    parser.add_option("-H", "--host",
                      help=f"Hostname of Flask app {default_host}.",
                      default=default_host)

    parser.add_option("-P", "--port",
                      help=f"Port for Flask app {default_port}.",
                      default=default_port)

    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug",
                      help=optparse.SUPPRESS_HELP)

    options, _ = parser.parse_args()

    application.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port)
    )
