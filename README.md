This example demonstrates the basics of using AWS's Elastic Beanstalk to deploy a web server which interacts 
with a worker tier environment.
To test this application, do the following:

1. Set up a web server environment and a worker environment in Elastic Beanstalk.
Take care to follow
the instructions in AWS's official documentation, particularly the IAM configuration for the worker.

2. In the AWS console go to Elastic Beanstalk -> your worker's environment name -> Configuration -> Worker Configuration
and change the "HTTP Path" variable from / to /worker.

3. Create a S3 bucket called "bwworker".
In this bucket create a file called "tasks" which contains the
string "task1 task2".
Create two more files in the bucket called "task1" and "task2", respectively,
and put a single integer in each file.

4. Deploy this application (together with the accompanying files "cron.yaml" and "requirements.txt") to
both your web server and worker environments.

Once this is done, periodically check the contents of the files "task1" and "task2" (using either the /read
endpoint of your web server or the AWS console).
If the application is working correctly, the numbers in 
these files should increase by 1 every minute.
You can also send messages to the worker via the web server's 
/web endpoint (see below).
(Note: the distinction between "Web server endpoints" and "Worker endpoints" made below is a bit artificial
if the application is deployed to both environments.
In production it would make more sense to deploy an
application with only the web server endpoints to the web server and another application with only the 
worker endpoints to the worker.
See the AWS article on the "Compose Environments API" for details on how
to conveniently manage multiple environments using awsebcli.)
