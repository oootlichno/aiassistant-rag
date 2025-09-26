import boto3

region = "us-east-2"

def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name=region)

def generate_with_bedrock(prompt, model="anthropic.claude-v2:1"):
    bedrock = get_bedrock_client()
    response = bedrock.invoke_model(
        modelId=model,
        body={
            "prompt": prompt,
            "max_tokens_to_sample": 500,
            "temperature": 0.3
        }
    )
    return response["body"].read().decode("utf-8")
