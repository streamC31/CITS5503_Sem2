import boto3

# Create AWS Rekognition client
rekognition = boto3.client('rekognition', region_name='ap-northeast-1')


def detect_labels(bucket_name, image_name):
    """
    Detect labels in an image stored in an S3 bucket.
    """
    response = rekognition.detect_labels(Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}}, MaxLabels=10)
    print(f"Detected labels in {image_name}:")
    for label in response['Labels']:
        print(f"Label: {label['Name']}, Confidence: {label['Confidence']:.2f}%")
    print()


def moderate_image(bucket_name, image_name):
    """
    Detect if an image contains inappropriate content using AWS Rekognition.
    """
    response = rekognition.detect_moderation_labels(Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}})
    print(f"Moderation labels for {image_name}:")
    if response['ModerationLabels']:
        for label in response['ModerationLabels']:
            print(f"Label: {label['Name']}, Confidence: {label['Confidence']:.2f}%")
    else:
        print(f"No inappropriate content found in {image_name}.")
    print()


def detect_faces(bucket_name, image_name):
    """
    Detect faces and facial attributes in an image using AWS Rekognition.
    """
    response = rekognition.detect_faces(Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}},
                                        Attributes=['ALL'])
    print(f"Detected faces in {image_name}:")
    for face_detail in response['FaceDetails']:
        print(f"Confidence: {face_detail['Confidence']:.2f}%")
        print(f"Age range: {face_detail['AgeRange']['Low']} - {face_detail['AgeRange']['High']}")
        print(f"Gender: {face_detail['Gender']['Value']} (Confidence: {face_detail['Gender']['Confidence']:.2f}%)")
        print(f"Emotions: {[emotion['Type'] for emotion in face_detail['Emotions'] if emotion['Confidence'] > 50]}")
        print()
    if not response['FaceDetails']:
        print(f"No faces detected in {image_name}.")
    print()


def detect_text(bucket_name, image_name):
    """
    Detect and extract text from an image using AWS Rekognition.
    """
    response = rekognition.detect_text(Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}})
    print(f"Detected text in {image_name}:")
    if response['TextDetections']:
        for text in response['TextDetections']:
            print(f"Detected: {text['DetectedText']}, Confidence: {text['Confidence']:.2f}%")
    else:
        print(f"No text found in {image_name}.")
    print()


if __name__ == '__main__':
    student_id = '23011392'
    bucket_name = f'{student_id}-lab9'

    # List of images to test
    images = ['urban.jpg', 'beach.jpg', 'faces.jpg', 'text.jpg']

    # Test each image using AWS Rekognition
    for image in images:
        # print(f"--- Processing {image} ---")
        #
        # # Detect text (only applicable for 'text.jpg')
        if image == 'text.jpg':
            detect_text(bucket_name, image)
