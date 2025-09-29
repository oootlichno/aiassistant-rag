import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

def ask_bedrock(prompt: str) -> str:
    body = {
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ],
        "max_tokens": 500,
    }

    response = bedrock.invoke_model(
        modelId=CLAUDE_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )
    output = json.loads(response["body"].read())
    return output["output"]["content"][0]["text"]

