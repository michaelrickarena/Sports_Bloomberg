import boto3
import sys

def main():
    s3 = boto3.client('s3', region_name='us-east-2')
    try:
        resp = s3.select_object_content(
            Bucket='sports-data-csv',
            Key='props/all_props_20250429230356.csv',
            ExpressionType='SQL',
            Expression="SELECT * FROM S3Object LIMIT 10",
            InputSerialization={'CSV': {}, 'CompressionType': 'NONE'},
            OutputSerialization={'CSV': {}},
        )
        # Stream out any returned records
        for event in resp['Payload']:
            if 'Records' in event:
                sys.stdout.buffer.write(event['Records']['Payload'])
        print()  # final newline
    except Exception as e:
        print("Error during S3 Select:", e)

if __name__ == "__main__":
    main()