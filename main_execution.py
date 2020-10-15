import praw
import csv
import json
import boto3
import os


# Function for finding new comments based on comment IDs. Takes two lists as x (new comment IDs) and y
# (old comment IDs). Returns true if new comments have been posted
def same_comm(x, y):
    newComm = False
    numComm = 0
    x_set = set(x)
    y_set = set(y)
    z_set = [x for x in x_set if x not in y_set]
    if(len(z_set) == 0):
        newComm = False
        return newComm, numComm, z_set
    else:
        newComm = True
        numComm = len(z_set)
        return newComm, numComm, z_set


# The main body of code for Lambda execution
def lambda_handler(event, context):
    reddit = praw.Reddit(client_id=os.environ['praw_client_id'],
                         client_secret=os.environ['praw_client_secret'],
                         user_agent=os.environ['praw_user_agent'])

    # Determines the redditor of interest. Instantiates two new arrays for storing comment information
    redditor1 = reddit.redditor(os.environ['target_redditor'])
    commsID = []
    commsBody = []

    # Pulls the comment IDs of the five newest comments posted by the redditor
    for comment in redditor1.comments.new(limit=5):
        commsID.append(comment.id)
        commsBody.append(comment.body)

    #Need to instantiate an s3 client
    s3_cli = boto3.client('s3')

    #Instantiates a client for AWS SNS
    sns_cli = boto3.client('sns')

    res_dict = s3_cli.get_object(Bucket=os.environ['s3_bucket_name'], Key='comments.csv')
    # TODO a lot of this file handling can be done with the io.BytesIO library instead of static files. Should change
    oldCommList = res_dict['Body'].read().decode('utf-8').split('\r\n')
    for i, x in enumerate(oldCommList):
        if x is '':
            oldCommList.pop(i)

    results = same_comm(commsID, oldCommList)

    # Sends a new message through AWS SNS if at least one new comment has been posted
    if results[0]:
        print('res[0] == True')
        # message = "You have " + str(results[1]) + " new briefings."
        message = 'You have {} new briefings.'.format(str(results[1]))

        response = sns_cli.publish(TargetArn=os.environ['sns_topic_arn'],
                                   Message=message,
                                   Subject="FRAGO")

        # Overwrites comments.csv with the new comment IDs, and uploads it to AWS S3
        # TODO same as above -- should change from static file handling to io.BytesIO in-memory file object
        with open('/tmp/comments.csv', 'w', newline='\n', encoding='utf-8') as csvfilewrite:
            csvfilewrite.truncate()
            spamwriter = csv.writer(csvfilewrite)
            for item in commsID:
                spamwriter.writerow([item])

        s3_cli.upload_file('/tmp/comments.csv', 'oproundup', 'comments.csv')
    else:
        # TODO add some logging to track that Trakkit actually ran and delivered a negative (no new comment) result
        print('Nah')

