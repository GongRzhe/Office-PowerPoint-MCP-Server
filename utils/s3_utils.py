"""
S3 storage utilities for PowerPoint MCP Server.
Functions for uploading and downloading presentations to/from S3-compatible storage.
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, Optional
import io
import os
from pptx import Presentation


def create_s3_client(
    endpoint_url: str,
    access_key: str,
    secret_key: str,
    region: Optional[str] = None
) -> boto3.client:
    """
    Create an S3 client for S3-compatible storage.
    
    Args:
        endpoint_url: The S3-compatible API endpoint URL
        access_key: Access key ID
        secret_key: Secret access key
        region: AWS region (optional, defaults to 'us-east-1')
        
    Returns:
        Configured boto3 S3 client
    """
    if region is None:
        region = 'us-east-1'
    
    return boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )


def upload_presentation_to_s3(
    presentation: Presentation,
    s3_client: boto3.client,
    bucket_name: str,
    object_key: str,
    metadata: Optional[Dict[str, str]] = None
) -> Dict:
    """
    Upload a PowerPoint presentation to S3-compatible storage.
    
    Args:
        presentation: The Presentation object to upload
        s3_client: Configured boto3 S3 client
        bucket_name: Name of the S3 bucket
        object_key: Object key (path) in the bucket
        metadata: Optional metadata to attach to the object
        
    Returns:
        Dictionary with upload result information
        
    Raises:
        ClientError: If upload fails
        NoCredentialsError: If credentials are invalid
    """
    try:
        # Save presentation to a BytesIO buffer
        buffer = io.BytesIO()
        presentation.save(buffer)
        buffer.seek(0)
        
        # Prepare upload arguments
        upload_args = {
            'Bucket': bucket_name,
            'Key': object_key,
            'Body': buffer,
            'ContentType': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        }
        
        # Add metadata if provided
        if metadata:
            upload_args['Metadata'] = metadata
        
        # Upload to S3
        s3_client.put_object(**upload_args)
        
        # Get object size
        buffer.seek(0, io.SEEK_END)
        size = buffer.tell()
        
        return {
            "success": True,
            "bucket": bucket_name,
            "key": object_key,
            "size_bytes": size,
            "message": f"Successfully uploaded presentation to s3://{bucket_name}/{object_key}"
        }
        
    except NoCredentialsError:
        raise ValueError("Invalid S3 credentials provided")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        raise Exception(f"S3 upload failed ({error_code}): {error_message}")
    except Exception as e:
        raise Exception(f"Failed to upload presentation to S3: {str(e)}")


def download_presentation_from_s3(
    s3_client: boto3.client,
    bucket_name: str,
    object_key: str
) -> Presentation:
    """
    Download a PowerPoint presentation from S3-compatible storage.
    
    Args:
        s3_client: Configured boto3 S3 client
        bucket_name: Name of the S3 bucket
        object_key: Object key (path) in the bucket
        
    Returns:
        Presentation object
        
    Raises:
        ClientError: If download fails
        NoCredentialsError: If credentials are invalid
    """
    try:
        # Download from S3 to a BytesIO buffer
        buffer = io.BytesIO()
        s3_client.download_fileobj(bucket_name, object_key, buffer)
        buffer.seek(0)
        
        # Load presentation from buffer
        presentation = Presentation(buffer)
        
        return presentation
        
    except NoCredentialsError:
        raise ValueError("Invalid S3 credentials provided")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'NoSuchKey':
            raise FileNotFoundError(f"Object not found: s3://{bucket_name}/{object_key}")
        elif error_code == 'NoSuchBucket':
            raise FileNotFoundError(f"Bucket not found: {bucket_name}")
        else:
            raise Exception(f"S3 download failed ({error_code}): {error_message}")
    except Exception as e:
        raise Exception(f"Failed to download presentation from S3: {str(e)}")


def list_s3_objects(
    s3_client: boto3.client,
    bucket_name: str,
    prefix: Optional[str] = None,
    max_keys: int = 100
) -> Dict:
    """
    List objects in an S3 bucket.
    
    Args:
        s3_client: Configured boto3 S3 client
        bucket_name: Name of the S3 bucket
        prefix: Optional prefix to filter objects
        max_keys: Maximum number of keys to return (default: 100)
        
    Returns:
        Dictionary with list of objects
        
    Raises:
        ClientError: If listing fails
    """
    try:
        list_args = {
            'Bucket': bucket_name,
            'MaxKeys': max_keys
        }
        
        if prefix:
            list_args['Prefix'] = prefix
        
        response = s3_client.list_objects_v2(**list_args)
        
        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    'key': obj['Key'],
                    'size_bytes': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag'].strip('"')
                })
        
        return {
            "bucket": bucket_name,
            "prefix": prefix or "",
            "object_count": len(objects),
            "objects": objects,
            "is_truncated": response.get('IsTruncated', False)
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'NoSuchBucket':
            raise FileNotFoundError(f"Bucket not found: {bucket_name}")
        else:
            raise Exception(f"S3 list failed ({error_code}): {error_message}")
    except Exception as e:
        raise Exception(f"Failed to list S3 objects: {str(e)}")


def delete_s3_object(
    s3_client: boto3.client,
    bucket_name: str,
    object_key: str
) -> Dict:
    """
    Delete an object from S3-compatible storage.
    
    Args:
        s3_client: Configured boto3 S3 client
        bucket_name: Name of the S3 bucket
        object_key: Object key (path) in the bucket
        
    Returns:
        Dictionary with deletion result
        
    Raises:
        ClientError: If deletion fails
    """
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        
        return {
            "success": True,
            "bucket": bucket_name,
            "key": object_key,
            "message": f"Successfully deleted s3://{bucket_name}/{object_key}"
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        raise Exception(f"S3 delete failed ({error_code}): {error_message}")
    except Exception as e:
        raise Exception(f"Failed to delete S3 object: {str(e)}")


def get_s3_object_metadata(
    s3_client: boto3.client,
    bucket_name: str,
    object_key: str
) -> Dict:
    """
    Get metadata for an S3 object.
    
    Args:
        s3_client: Configured boto3 S3 client
        bucket_name: Name of the S3 bucket
        object_key: Object key (path) in the bucket
        
    Returns:
        Dictionary with object metadata
        
    Raises:
        ClientError: If operation fails
    """
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
        
        return {
            "bucket": bucket_name,
            "key": object_key,
            "size_bytes": response['ContentLength'],
            "last_modified": response['LastModified'].isoformat(),
            "content_type": response.get('ContentType', 'unknown'),
            "etag": response['ETag'].strip('"'),
            "metadata": response.get('Metadata', {})
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == '404' or error_code == 'NoSuchKey':
            raise FileNotFoundError(f"Object not found: s3://{bucket_name}/{object_key}")
        else:
            raise Exception(f"S3 head object failed ({error_code}): {error_message}")
    except Exception as e:
        raise Exception(f"Failed to get S3 object metadata: {str(e)}")
