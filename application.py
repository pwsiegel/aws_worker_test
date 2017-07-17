from flask import Flask, request
import boto3, botocore
import json

application = Flask(__name__)

#---Web server endpoints---#

@application.route("/")
def home():
	return "Server Loaded"

@application.route("/web")
def send_to_worker():
	'''
	Handles a GET request of the form /web?file=myfile&message=mymessage.
	The web server sends the json {"file": "myfile", "message": "mymessage"} to the worker tier (via its SQS queue)
	for processing.
	'''
	try:
		data = json.dumps({"file": request.args["file"], "message": request.args["message"]})
	except KeyError as e:
		return str(e)

	try:
		queue = boto3.resource("sqs", region_name="us-east-1").get_queue_by_name(
			QueueName = "your worker's queue's name goes here")
		response = queue.send_message(MessageBody = data)
	except botocore.exceptions.ClientError as e:
		return str(e)

	return data

@application.route("/read")
def get_from_s3():
	return read_s3(request.args["file"])

#---Worker endpoints---$

@application.route("/worker", methods = ["POST"])
def worker():
	'''
	Takes a JSON of the form {"file": "myfile", "message": "mymessage"} and writes "mymessage" to a file named
	"myfile" in the S3 bucket "bwworker".
	The JSON is sent to the worker by submitting a POST request to the worker's SQS queue. (Though note that if
	this application is deployed to both the web server and the worker then it is possible to POST directly
	to the web server.)
	Important: by default the worker's SQS queue will POST to the URL "/"; to change it to "/worker", change the
	worker's HTTP Path setting (found in AWS console -> Elastic Beanstalk -> your worker's environment name -> 
	Configuration -> Worker Configuration)
	'''
	data = request.get_json()
	return write_s3(data["file"], data["message"])

@application.route("/tasks", methods = ["POST"])
def tasks():
	'''
	Opens the file "tasks" in the S3 bucket "bwworker", reads whitespace delimited file names, and for each
	file name reads an integer from the file, adds 1, and writes the result.
	This URL is called automatically at time(s) specified in the file "cron.yaml" in the same directory as 
	this application.  (As above, note that if this application is deployed to the web server as well as the
	worker then it is possible to POST directly to the web server.)
	'''
	task_list = read_s3("tasks").split()

	for task in task_list:
		num = int(read_s3(task)) + 1
		write_s3(task, num)

	return str(task_list)

#---S3 I/O---#

def read_s3(file_name):
	try:
		return boto3.resource("s3").Object(bucket_name = "bwworker", key = file_name).get()["Body"].read().decode("utf-8")
	except botocore.exceptions.ClientError as e:
		return str(e)

def write_s3(file_name, message):
	try:
		boto3.resource("s3").Bucket("bwworker").put_object(Key = file_name, Body = str(message))
		return "Message sent"
	except botocore.exceptions.ClientError as e:
		return str(e)

if __name__ == "__main__":
	application.run(debug = True)



