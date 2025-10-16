"""
S3 storage tools for PowerPoint MCP Server.
Handles uploading, downloading, and managing presentations in S3-compatible storage.
"""
from typing import Dict, Optional
from mcp.server.fastmcp import FastMCP
import utils.s3_utils as s3_utils


# Global S3 client cache
_s3_clients = {}


def register_s3_tools(app: FastMCP, presentations: Dict, get_current_presentation_id):
    """Register S3 storage tools with the FastMCP app"""
    
    @app.tool()
    def configure_s3_connection(
        connection_name: str,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        region: Optional[str] = None
    ) -> Dict:
        """
        Configure an S3-compatible storage connection.
        
        This creates a reusable S3 client configuration that can be referenced by name
        in other S3 operations. Supports AWS S3, MinIO, DigitalOcean Spaces, and other
        S3-compatible storage services.
        
        Args:
            connection_name: A unique name for this connection (e.g., 'production', 'backup')
            endpoint_url: The S3-compatible API endpoint URL (e.g., 'https://s3.amazonaws.com')
            access_key: Access key ID for authentication
            secret_key: Secret access key for authentication
            region: AWS region (optional, defaults to 'us-east-1')
            
        Returns:
            Dictionary with connection configuration result
            
        Examples:
            - AWS S3: endpoint_url='https://s3.amazonaws.com', region='us-east-1'
            - MinIO: endpoint_url='http://localhost:9000', region='us-east-1'
            - DigitalOcean Spaces: endpoint_url='https://nyc3.digitaloceanspaces.com', region='nyc3'
        """
        try:
            # Create S3 client
            s3_client = s3_utils.create_s3_client(
                endpoint_url=endpoint_url,
                access_key=access_key,
                secret_key=secret_key,
                region=region
            )
            
            # Store in global cache
            _s3_clients[connection_name] = s3_client
            
            return {
                "success": True,
                "connection_name": connection_name,
                "endpoint_url": endpoint_url,
                "region": region or 'us-east-1',
                "message": f"S3 connection '{connection_name}' configured successfully"
            }
            
        except Exception as e:
            return {
                "error": f"Failed to configure S3 connection: {str(e)}"
            }
    
    @app.tool()
    def upload_presentation_to_s3(
        bucket_name: str,
        object_key: str,
        connection_name: str = "default",
        presentation_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Upload a presentation to S3-compatible storage.
        
        Args:
            bucket_name: Name of the S3 bucket
            object_key: Object key (path) in the bucket (e.g., 'presentations/my-deck.pptx')
            connection_name: Name of the S3 connection to use (default: 'default')
            presentation_id: ID of the presentation to upload (uses current if not specified)
            metadata: Optional metadata to attach to the object (key-value pairs)
            
        Returns:
            Dictionary with upload result
        """
        # Check if connection exists
        if connection_name not in _s3_clients:
            return {
                "error": f"S3 connection '{connection_name}' not found. Please configure it first using configure_s3_connection."
            }
        
        # Get presentation
        pres_id = presentation_id if presentation_id is not None else get_current_presentation_id()
        
        if pres_id is None or pres_id not in presentations:
            return {
                "error": "No presentation is currently loaded or the specified ID is invalid"
            }
        
        try:
            # Upload to S3
            result = s3_utils.upload_presentation_to_s3(
                presentation=presentations[pres_id],
                s3_client=_s3_clients[connection_name],
                bucket_name=bucket_name,
                object_key=object_key,
                metadata=metadata
            )
            
            result["presentation_id"] = pres_id
            result["connection_name"] = connection_name
            return result
            
        except Exception as e:
            return {
                "error": f"Failed to upload presentation: {str(e)}"
            }
    
    @app.tool()
    def download_presentation_from_s3(
        bucket_name: str,
        object_key: str,
        connection_name: str = "default",
        id: Optional[str] = None
    ) -> Dict:
        """
        Download a presentation from S3-compatible storage.
        
        Args:
            bucket_name: Name of the S3 bucket
            object_key: Object key (path) in the bucket
            connection_name: Name of the S3 connection to use (default: 'default')
            id: Optional ID to assign to the downloaded presentation
            
        Returns:
            Dictionary with download result
        """
        # Check if connection exists
        if connection_name not in _s3_clients:
            return {
                "error": f"S3 connection '{connection_name}' not found. Please configure it first using configure_s3_connection."
            }
        
        try:
            # Download from S3
            pres = s3_utils.download_presentation_from_s3(
                s3_client=_s3_clients[connection_name],
                bucket_name=bucket_name,
                object_key=object_key
            )
            
            # Generate an ID if not provided
            if id is None:
                id = f"presentation_{len(presentations) + 1}"
            
            # Store the presentation
            presentations[id] = pres
            
            return {
                "success": True,
                "presentation_id": id,
                "bucket": bucket_name,
                "key": object_key,
                "connection_name": connection_name,
                "slide_count": len(pres.slides),
                "message": f"Successfully downloaded presentation from s3://{bucket_name}/{object_key}"
            }
            
        except FileNotFoundError as e:
            return {
                "error": str(e)
            }
        except Exception as e:
            return {
                "error": f"Failed to download presentation: {str(e)}"
            }
    
    @app.tool()
    def list_s3_presentations(
        bucket_name: str,
        connection_name: str = "default",
        prefix: Optional[str] = None,
        max_keys: int = 100
    ) -> Dict:
        """
        List presentations in an S3 bucket.
        
        Args:
            bucket_name: Name of the S3 bucket
            connection_name: Name of the S3 connection to use (default: 'default')
            prefix: Optional prefix to filter objects (e.g., 'presentations/')
            max_keys: Maximum number of objects to return (default: 100)
            
        Returns:
            Dictionary with list of objects
        """
        # Check if connection exists
        if connection_name not in _s3_clients:
            return {
                "error": f"S3 connection '{connection_name}' not found. Please configure it first using configure_s3_connection."
            }
        
        try:
            result = s3_utils.list_s3_objects(
                s3_client=_s3_clients[connection_name],
                bucket_name=bucket_name,
                prefix=prefix,
                max_keys=max_keys
            )
            
            result["connection_name"] = connection_name
            return result
            
        except Exception as e:
            return {
                "error": f"Failed to list S3 objects: {str(e)}"
            }
    
    @app.tool()
    def delete_s3_presentation(
        bucket_name: str,
        object_key: str,
        connection_name: str = "default"
    ) -> Dict:
        """
        Delete a presentation from S3-compatible storage.
        
        Args:
            bucket_name: Name of the S3 bucket
            object_key: Object key (path) in the bucket
            connection_name: Name of the S3 connection to use (default: 'default')
            
        Returns:
            Dictionary with deletion result
        """
        # Check if connection exists
        if connection_name not in _s3_clients:
            return {
                "error": f"S3 connection '{connection_name}' not found. Please configure it first using configure_s3_connection."
            }
        
        try:
            result = s3_utils.delete_s3_object(
                s3_client=_s3_clients[connection_name],
                bucket_name=bucket_name,
                object_key=object_key
            )
            
            result["connection_name"] = connection_name
            return result
            
        except Exception as e:
            return {
                "error": f"Failed to delete S3 object: {str(e)}"
            }
    
    @app.tool()
    def get_s3_presentation_info(
        bucket_name: str,
        object_key: str,
        connection_name: str = "default"
    ) -> Dict:
        """
        Get metadata for a presentation in S3-compatible storage.
        
        Args:
            bucket_name: Name of the S3 bucket
            object_key: Object key (path) in the bucket
            connection_name: Name of the S3 connection to use (default: 'default')
            
        Returns:
            Dictionary with object metadata
        """
        # Check if connection exists
        if connection_name not in _s3_clients:
            return {
                "error": f"S3 connection '{connection_name}' not found. Please configure it first using configure_s3_connection."
            }
        
        try:
            result = s3_utils.get_s3_object_metadata(
                s3_client=_s3_clients[connection_name],
                bucket_name=bucket_name,
                object_key=object_key
            )
            
            result["connection_name"] = connection_name
            return result
            
        except FileNotFoundError as e:
            return {
                "error": str(e)
            }
        except Exception as e:
            return {
                "error": f"Failed to get S3 object metadata: {str(e)}"
            }
    
    @app.tool()
    def list_s3_connections() -> Dict:
        """
        List all configured S3 connections.
        
        Returns:
            Dictionary with list of connection names
        """
        return {
            "connections": list(_s3_clients.keys()),
            "count": len(_s3_clients)
        }
