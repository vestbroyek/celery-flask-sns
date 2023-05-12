# Using Celery, Flask, and AWS SNS for event-driven workloads
This repo is just a quick tutorial on how to run event-driven workloads using Celery, Flask, and SNS. We'll use S3 Events as the producer in this pub-sub model but we can also talk to our HTTP endpoint directly.

## Prerequisites
As prerequisites, you need to have 
- Celery, Flask, and Redis installed
- A way to expose a public HTTP endpoint, e.g. by launching an EC2 instance
- An SNS queue

## Walkthrough
First, launch an EC2 instance. Get pip to install Flask and celery and also install Redis (the installation will vary based on the AMI you use. I used an Ubuntu AMI.

Make sure you can SSH into the instance and that it can receive HTTP traffic. You can either configure the Flask app to listen on port 80 or, in my case, set a Custom TCP rule to allow traffic on port 5001 from anywhere.

Create app.py, which will contain our Flask app as well as the definition of our celery task. An example app.py is provided.

Two endpoints are defined: / and /sns. The /sns endpoint is necessary for confirming the SNS subscription. In SNS, create a new subscription that uses your instance's DNS, using HTTP, and using the /sns endpoint. Use HTTP and a URL like http://ec2-13-41-73-72.eu-west-2.compute.amazonaws.com:5001/sns. Then confirm the subscription. 

Now we can define any endpoints we want, for example, we can use /. Ensure / allows the POST method, as that's how we'll receive notifications from SNS. In my case, it'll just say "Hello from Flask for the i-th time" a 100 times.

Now we can run Redis and Celery. We will use Redis as the broker. Simply start Redis, e.g.`sudo systemctl restart redis.service`. Run `redis-cli ping` to check it works - if it returns PONG, it works.

Now run Celery with `celery -A app.celery worker --loglevel=info`. 

At this point, we have
- An HTTP endpoint exposed that can receive traffic over the public internet
- This endpoint, `/`, will use Redis to send tasks to Celery
- A Celery worker ready to execute our tasks!

Simply navigate to your endpoint, http://ec2-13-41-73-72.eu-west-2.compute.amazonaws.com:5001/ (your DNS will be different, of course, or use the Public IPv4). Notice we now use `/` as the endpoint, not `/sns`. It will only work if you allow GET as a method on the endpoint, but it will work. 

Finally, we want to trigger our jobs through SNS. I created a bucket, which will have an S3 Event. This means that as soon as I create a file with a certain prefix, a message will be sent to SNS, which will then send a message to the HTTP endpoint, in turn triggering Celery to execute our task. 

Now we can customise our workflow as we see fit. 

The main next steps would be to use HTTPS as it's more secure.
