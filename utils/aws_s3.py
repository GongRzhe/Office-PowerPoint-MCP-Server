# utils/aws_s3.py
import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv

# .env を読み込んで環境変数にする
load_dotenv()

# 環境変数から AWS 認証情報取得
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")

def s3_client():
    """
    認証情報 + region を使って boto3 の S3 クライアントを返す。
    .env や環境変数で設定してあればそれを使う。
    """
    # boto3 に渡す引数は重複させない
    client_kwargs = {
        "region_name": AWS_REGION,
        "config": Config(signature_version="s3v4")
    }
    # アクセスキー情報が設定されていればそれも渡す
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        client_kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
        client_kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY

    return boto3.client("s3", **client_kwargs)

def get_bytes(bucket: str, key: str) -> bytes:
    """
    指定したバケット＋キーのオブジェクトを取得して bytes を返す
    """
    return s3_client().get_object(Bucket=bucket, Key=key)["Body"].read()
