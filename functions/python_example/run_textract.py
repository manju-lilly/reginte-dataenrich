import json
import boto3
import time

from trp import Document

s3_bucket_name = "lly-reg-intel-raw-zone-dev"

## initialize aws textract client
textract = boto3.client('textract')

def lambda_handler(event, context):
        
    # TODO implement
    type_op = 1
    s3_urls = event['s3_urls']
    
    for s3_url in s3_urls:
        document_key = s3_url
        jobId = startJob(type_op, s3_bucket_name, document_key)
        print("Started job with id:{}".format(jobId))
        
        if(isJobComplete(type_op, jobId)):
            response = get_job_results(type_op, jobId)
            doc = Document(response)
            lines(document_key, doc)
            
        
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def startJob(type_op, s3_bucket_name, document_key):
    response = None
    if type_op == 1:
        response = textract.start_document_text_detection(DocumentLocation = {
            'S3Object':{
                'Bucket': s3_bucket_name,
                'Name': document_key
            }
        })
    else:
        response = cient.start_document_analysis(DocumentLocation  = {
            'S3Object':{
                'Bucket': s3_bucket_name,
                'Name': document_key
            }
        }, FeatureTypes=['FORMS', 'TABLES'])
        
    return response['JobId']
    
    
def isJobComplete(type_op, jobId):
    time.sleep(5)
    
    if type_op == 1:
        response = textract.get_document_text_detection(JobId = jobId)
    else:
        response = textract.get_document_analysis(JobId = jobId )
        
    status = response['JobStatus']
    print("Job status:{}".format(status))
    
    while(status == 'IN_PROGRESS'):
        time.sleep(5)
        
        if type_op == 1:
            response = textract.get_document_text_detection(JobId = jobId)
        else:
            response = textract.get_document_analysis(JobId = jobId )
            
        status = response['JobStatus']
        print("Job status:{}".format(status))
        
    return status
    
    
def get_job_results(type_op, jobId):
    pages = []
    time.sleep(5)
    
    client = boto3.client('textract')
    
    if type_op == 1:
        response = client.get_document_text_detection(JobId = jobId)
    else:
        response = client.get_document_analysis(JobId = jobId)
        
    pages.append(response)
    
    print("Result set page received: {}".format(len(pages)))
    
    nextToken = None
    if('NextToken' in response):
        nextToken  = response['NextToken']
        
    while(nextToken):
        time.sleep(5)
        
        if type_op ==1:
            response =  client.get_document_text_detection(JobId = jobId, NextToken = nextToken)
        else:
            response = client.get_document_analysis(JobId = jobId, NextToken = nextToken)
            
        print("Result set page received: {}".format(len(pages)))
        pages.append(response)
        
        nextToken = None
        if('NextToken' in response):
            nextToken  = response['NextToken']
        
    
    return pages
    
def lines(document_key, doc):
    filename = document_key + "-lines.txt"
    print(filename)
    lines = []
    for page in doc.pages:
        for line in page.lines:
            print("Line: {} - {}".format(line.text, line.confidence))
            lines.append("{}".format(line.text) + "\n")
    
    save_file(lines,filename)
    return
    
    
def save_file(res, url):
    documentName = url
    s3_client = boto3.client('s3')
    response = s3_client.put_object(Bucket=s3_bucket_name, Key=documentName, Body="".join(res))
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    
    print("Saved document ", url)
    return status_code
    
