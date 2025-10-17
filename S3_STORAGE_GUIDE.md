# S3 Storage Guide - PowerPoint MCP Server

## Overview

The PowerPoint MCP Server now supports uploading, downloading, and managing presentations in S3-compatible storage services. This feature enables cloud-based presentation storage and retrieval, making it easy to integrate with AWS S3, MinIO, DigitalOcean Spaces, and other S3-compatible services.

## Features

- **Upload presentations** to S3-compatible storage
- **Download presentations** from S3-compatible storage
- **List presentations** in S3 buckets
- **Delete presentations** from S3 storage
- **Get metadata** for stored presentations
- **Multiple connection support** - configure and manage multiple S3 connections
- **Custom metadata** - attach custom metadata to uploaded presentations

## Supported Storage Services

- **AWS S3** - Amazon's object storage service
- **MinIO** - Self-hosted S3-compatible storage
- **DigitalOcean Spaces** - DigitalOcean's object storage
- **Backblaze B2** - Cloud storage with S3-compatible API
- **Wasabi** - Hot cloud storage
- **Any S3-compatible service** - Any service implementing the S3 API

## Installation

The S3 feature requires the `boto3` library, which is included in the updated `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables (Recommended)

The server automatically configures a default S3 connection from environment variables. This is the recommended approach for production deployments.

**Supported Environment Variables:**

- `S3_ENDPOINT_URL` - S3 endpoint URL (required)
- `S3_ACCESS_KEY` or `AWS_ACCESS_KEY_ID` - Access key ID
- `S3_SECRET_KEY` or `AWS_SECRET_ACCESS_KEY` - Secret access key
- `S3_REGION` or `AWS_DEFAULT_REGION` - AWS region (optional, defaults to 'us-east-1')

**Setup:**

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your S3 credentials:
```bash
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_REGION=us-east-1
```

3. Start the server - it will automatically configure the default connection:
```bash
python ppt_mcp_server.py
```

**Example Configurations:**

AWS S3:
```bash
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
S3_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_REGION=us-east-1
```

MinIO (Local):
```bash
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_REGION=us-east-1
```

DigitalOcean Spaces:
```bash
S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
S3_ACCESS_KEY=your-spaces-key
S3_SECRET_KEY=your-spaces-secret
S3_REGION=nyc3
```

### Manual Configuration

You can also configure connections manually using the `configure_s3_connection` tool. This is useful for:
- Multiple connections to different S3 services
- Runtime configuration changes
- Testing different configurations

## Available Tools

### 1. configure_s3_connection

Configure an S3-compatible storage connection.

**Parameters:**
- `connection_name` (string, required): A unique name for this connection (e.g., 'production', 'backup')
- `endpoint_url` (string, required): The S3-compatible API endpoint URL
- `access_key` (string, required): Access key ID for authentication
- `secret_key` (string, required): Secret access key for authentication
- `region` (string, optional): AWS region (defaults to 'us-east-1')

**Examples:**

```python
# AWS S3
configure_s3_connection(
    connection_name="aws-production",
    endpoint_url="https://s3.amazonaws.com",
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
    region="us-east-1"
)

# MinIO (local)
configure_s3_connection(
    connection_name="minio-local",
    endpoint_url="http://localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    region="us-east-1"
)

# DigitalOcean Spaces
configure_s3_connection(
    connection_name="do-spaces",
    endpoint_url="https://nyc3.digitaloceanspaces.com",
    access_key="YOUR_SPACES_KEY",
    secret_key="YOUR_SPACES_SECRET",
    region="nyc3"
)
```

### 2. upload_presentation_to_s3

Upload a presentation to S3-compatible storage.

**Parameters:**
- `bucket_name` (string, required): Name of the S3 bucket
- `object_key` (string, required): Object key (path) in the bucket (e.g., 'presentations/my-deck.pptx')
- `connection_name` (string, optional): Name of the S3 connection to use (default: 'default')
- `presentation_id` (string, optional): ID of the presentation to upload (uses current if not specified)
- `metadata` (dict, optional): Optional metadata to attach to the object

**Example:**

```python
upload_presentation_to_s3(
    bucket_name="my-presentations",
    object_key="2024/Q4/sales-deck.pptx",
    connection_name="aws-production",
    metadata={
        "author": "John Doe",
        "department": "Sales",
        "version": "1.0"
    }
)
```

### 3. download_presentation_from_s3

Download a presentation from S3-compatible storage.

**Parameters:**
- `bucket_name` (string, required): Name of the S3 bucket
- `object_key` (string, required): Object key (path) in the bucket
- `connection_name` (string, optional): Name of the S3 connection to use (default: 'default')
- `id` (string, optional): Optional ID to assign to the downloaded presentation

**Example:**

```python
download_presentation_from_s3(
    bucket_name="my-presentations",
    object_key="2024/Q4/sales-deck.pptx",
    connection_name="aws-production",
    id="sales-deck-q4"
)
```

### 4. list_s3_presentations

List presentations in an S3 bucket.

**Parameters:**
- `bucket_name` (string, required): Name of the S3 bucket
- `connection_name` (string, optional): Name of the S3 connection to use (default: 'default')
- `prefix` (string, optional): Optional prefix to filter objects (e.g., 'presentations/')
- `max_keys` (int, optional): Maximum number of objects to return (default: 100)

**Example:**

```python
list_s3_presentations(
    bucket_name="my-presentations",
    prefix="2024/Q4/",
    connection_name="aws-production",
    max_keys=50
)
```

### 5. delete_s3_presentation

Delete a presentation from S3-compatible storage.

**Parameters:**
- `bucket_name` (string, required): Name of the S3 bucket
- `object_key` (string, required): Object key (path) in the bucket
- `connection_name` (string, optional): Name of the S3 connection to use (default: 'default')

**Example:**

```python
delete_s3_presentation(
    bucket_name="my-presentations",
    object_key="2024/Q4/old-deck.pptx",
    connection_name="aws-production"
)
```

### 6. get_s3_presentation_info

Get metadata for a presentation in S3-compatible storage.

**Parameters:**
- `bucket_name` (string, required): Name of the S3 bucket
- `object_key` (string, required): Object key (path) in the bucket
- `connection_name` (string, optional): Name of the S3 connection to use (default: 'default')

**Example:**

```python
get_s3_presentation_info(
    bucket_name="my-presentations",
    object_key="2024/Q4/sales-deck.pptx",
    connection_name="aws-production"
)
```

### 7. list_s3_connections

List all configured S3 connections.

**Parameters:** None

**Example:**

```python
list_s3_connections()
```

## Usage Workflow

### Basic Workflow

1. **Configure a connection:**
```python
configure_s3_connection(
    connection_name="default",
    endpoint_url="https://s3.amazonaws.com",
    access_key="YOUR_KEY",
    secret_key="YOUR_SECRET"
)
```

2. **Create or load a presentation:**
```python
create_presentation(id="my-presentation")
add_slide(layout_index=0)
add_text_to_slide(slide_index=0, text="Hello S3!", left=1, top=1, width=8, height=1)
```

3. **Upload to S3:**
```python
upload_presentation_to_s3(
    bucket_name="my-bucket",
    object_key="presentations/hello.pptx",
    presentation_id="my-presentation"
)
```

4. **Download from S3:**
```python
download_presentation_from_s3(
    bucket_name="my-bucket",
    object_key="presentations/hello.pptx",
    id="downloaded-presentation"
)
```

### Advanced Workflow with Multiple Connections

```python
# Configure production connection
configure_s3_connection(
    connection_name="production",
    endpoint_url="https://s3.amazonaws.com",
    access_key="PROD_KEY",
    secret_key="PROD_SECRET",
    region="us-east-1"
)

# Configure backup connection
configure_s3_connection(
    connection_name="backup",
    endpoint_url="https://nyc3.digitaloceanspaces.com",
    access_key="BACKUP_KEY",
    secret_key="BACKUP_SECRET",
    region="nyc3"
)

# Upload to production
upload_presentation_to_s3(
    bucket_name="prod-presentations",
    object_key="2024/important-deck.pptx",
    connection_name="production"
)

# Also upload to backup
upload_presentation_to_s3(
    bucket_name="backup-presentations",
    object_key="2024/important-deck.pptx",
    connection_name="backup"
)
```

## Security Best Practices

1. **Never hardcode credentials** - Use environment variables or secure credential management
2. **Use IAM roles** when running on AWS EC2/ECS/Lambda
3. **Implement least privilege** - Grant only necessary S3 permissions
4. **Enable encryption** - Use server-side encryption for sensitive presentations
5. **Use HTTPS** - Always use HTTPS endpoints for production
6. **Rotate credentials** regularly
7. **Monitor access** - Enable S3 access logging

## Environment Variables

You can use environment variables for S3 credentials:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

## Error Handling

The S3 tools provide detailed error messages:

- **Connection errors**: "S3 connection 'name' not found"
- **Authentication errors**: "Invalid S3 credentials provided"
- **Not found errors**: "Object not found: s3://bucket/key"
- **Permission errors**: "S3 upload failed (AccessDenied): ..."

## Performance Considerations

- **Large files**: Uploads/downloads are done in-memory, so be mindful of presentation sizes
- **Concurrent operations**: Multiple S3 operations can be performed concurrently
- **Network latency**: Consider using S3 endpoints in the same region as your application
- **Caching**: Downloaded presentations are stored in memory for reuse

## Troubleshooting

### Connection Issues

**Problem**: "Failed to configure S3 connection"
**Solution**: Verify endpoint URL format and network connectivity

### Authentication Issues

**Problem**: "Invalid S3 credentials provided"
**Solution**: Check access key and secret key are correct

### Upload/Download Issues

**Problem**: "S3 upload failed (NoSuchBucket)"
**Solution**: Verify bucket exists and you have access

**Problem**: "Object not found"
**Solution**: Check object key spelling and path

## Examples

### Complete Example: Backup Workflow

```python
# 1. Configure S3 connection
configure_s3_connection(
    connection_name="backup",
    endpoint_url="https://s3.amazonaws.com",
    access_key="YOUR_KEY",
    secret_key="YOUR_SECRET",
    region="us-west-2"
)

# 2. Create a presentation
create_presentation(id="quarterly-report")
add_slide(layout_index=0)
add_text_to_slide(
    slide_index=0,
    text="Q4 2024 Report",
    left=1,
    top=1,
    width=8,
    height=2
)

# 3. Upload to S3 with metadata
upload_presentation_to_s3(
    bucket_name="company-presentations",
    object_key="reports/2024/Q4-report.pptx",
    connection_name="backup",
    metadata={
        "quarter": "Q4",
        "year": "2024",
        "department": "Finance"
    }
)

# 4. List all reports
reports = list_s3_presentations(
    bucket_name="company-presentations",
    prefix="reports/2024/",
    connection_name="backup"
)

# 5. Get metadata for a specific report
info = get_s3_presentation_info(
    bucket_name="company-presentations",
    object_key="reports/2024/Q4-report.pptx",
    connection_name="backup"
)
```

## Version History

- **v2.2.0** - Initial S3 storage support
  - 7 new S3 tools
  - Support for multiple S3-compatible services
  - Custom metadata support
  - Multiple connection management

## Support

For issues or questions about S3 storage:
1. Check this guide for common solutions
2. Verify your S3 credentials and permissions
3. Test connectivity to your S3 endpoint
4. Review error messages for specific issues

## Future Enhancements

Planned features for future releases:
- Multipart upload for large files
- Presigned URL generation
- S3 bucket creation and management
- Automatic retry with exponential backoff
- Progress callbacks for large uploads/downloads
- S3 Select support for querying presentation metadata
