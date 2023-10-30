import boto3
from app.config import settings


class CashifySQS:
    """
    Cashify SQS class to handle all SQS functionalities.
    """

    sqs = None
    queue = None

    def __init__(self, queue_name: str):
        # Get the service resource
        sqs_client = boto3.client('sqs')
        # Get the queue. This returns an SQS.Queue instance
        queue_url = sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']

        self.sqs = boto3.resource('sqs')
        self.queue = self.sqs.Queue(queue_url)

    def push(self, message_body: any, message_attributes: dict = None, delay_in_seconds: int = 0):
        """
        method to push the message to queue
        """
        try:
            if not message_attributes:
                message_attributes = {}
            response = self.queue.send_message(
                MessageBody=message_body,
                MessageAttributes=message_attributes,
                DelaySeconds=delay_in_seconds
            )
            return response
        except Exception as e:
            print(e)
            return None

    def poll(self, message_attributes: list = None, attributes: list = None, no_of_messages: int = 10):
        """
        method to poll the message from queue
        """
        try:
            if no_of_messages > 10:
                raise Exception('Number of messages must not exceed 10.')
            if not message_attributes:
                message_attributes = ['All']
            if not attributes:
                attributes = ['All']
            response = self.queue.receive_messages(
                AttributeNames=attributes,
                MessageAttributeNames=message_attributes,
                MaxNumberOfMessages=no_of_messages,
                WaitTimeSeconds=0
            )
            return response
        except Exception as e:
            print(e)
            return None

    def delete(self, receipt_handle: list):
        """
        method to delete the message from queue
        """
        pass
