import os
from dotenv import load_dotenv
import asyncio
from courses import Courses
import boto3

# Load environment variables (for example, from a .env file)
load_dotenv()
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

def publish_notification(course_name: str, message: str):
    print("Loaded SNS_TOPIC_ARN:", SNS_TOPIC_ARN)
    sns_client = boto3.client('sns', region_name='us-east-1')
    try:
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=f"Course Alert: {course_name}"
        )
        print(f"Published notification for {course_name}; MessageId: {response.get('MessageId')}")
    except Exception as e:
        print(f"Error publishing notification for {course_name}: {e}")

async def main():
    # Read courses from the text file.
    courses = Courses.read_from_txt_file('courses.txt')

    # Update course availabilities and capture any changes.
    changes = courses.update_all_availability()
    print("Changes:", changes)

    # For each course with changes, generate a notification message and publish it via SNS.
    if changes:
        for crn, change in changes.items():
            if not change:
                continue
            course = courses.find_course(crn)
            if course is None:
                continue
            message = course.generate_message(change)
            print("Generated message:", message)
            if message:
                publish_notification(course.name, message)

    # Save the updated course state for future invocations.
    courses.save_to_file()

def lambda_handler(event, context):
    """
    AWS Lambda handler function. This function is invoked each time the Lambda is triggered.
    It runs an asynchronous main() function and returns a status code indicating success or error.
    """
    try:
        asyncio.run(main())
        return {
            "statusCode": 200,
            "body": "Lambda executed successfully"
        }
    except Exception as e:
        print("Error in lambda_handler:", e)
        return {
            "statusCode": 500,
            "body": str(e)
        }

if __name__ == '__main__':
    # For local testing, simply run the main function.
    asyncio.run(main())
