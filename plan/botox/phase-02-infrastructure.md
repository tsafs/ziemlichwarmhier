---
goal: "Phase 2: Infrastructure Setup - Hetzner Object Storage & CDN Configuration"
version: 1.0
date_created: 2026-02-16
last_updated: 2026-02-16
owner: Sebastian
status: 'Planned'
tags: [phase-2, infrastructure, storage, hetzner, cdn, cloudflare, s3]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan details the infrastructure setup for the ERA5-Land Germany Climate Visualization project. It establishes Hetzner Object Storage for tile hosting and configures the existing Cloudflare CDN for caching. This phase creates the foundation for all data pipelines and frontend tile loading.

**Key Deliverables:**
- Hetzner Object Storage bucket configured for public tile serving
- CORS configuration for browser-based tile loading
- Environment variable schema and `.env.example` template
- Reusable S3-compatible upload utility adapted for Hetzner
- Infrastructure setup script for reproducible configuration
- Integration test to verify bucket accessibility

**Expected Duration:** 2-4 hours

## 0. Preflight & Self-Correction

> **Mandatory gate**: Before starting any task in this phase and after every change, run the preflight script and follow the self-correction loop.

1. **Run preflight**: `./scripts/run-preflight.sh` — all checks must pass before starting work
2. **After each change**: re-run preflight or the targeted test subset (see `docs/self-correct-playbook.md`)
3. **On failure**: follow retry guidance in the playbook (max 3 attempts per issue, then revert and re-analyze)
4. **Local CI parity**: optionally run `./scripts/act-local.sh build` to verify GHA workflows locally (requires Docker + act)

## 1. Requirements & Constraints

### Requirements (from Master Plan)

- **REQ-P2-001**: ERA5-Land tiles must be publicly accessible via HTTPS
- **REQ-INF-002**: Storage must support S3-compatible API (boto3)
- **REQ-INF-003**: Free or near-zero egress costs (Hetzner: free outbound)
- **REQ-INF-004**: EU-based storage for GDPR compliance
- **REQ-INF-005**: Support for content-type headers (WebP tiles)
- **REQ-INF-006**: CDN caching for performance (Cloudflare existing)

### Non-Functional Requirements

- **NFR-P2-001**: Monthly costs ≤ €5 for storage (Hetzner: €0.0052/GB)
- **NFR-P2-002**: Tile requests < 500ms latency (with CDN)
- **NFR-P2-003**: 99.9% availability for tile serving

### Constraints

- **CON-P2-001**: Hetzner Object Storage uses S3-compatible API
- **CON-P2-002**: Hetzner endpoint format: `https://<bucket>.<location>.your-objectstorage.com`
- **CON-P2-003**: Supported locations: fsn1 (Falkenstein), nbg1 (Nuremberg), hel1 (Helsinki)
- **CON-P2-004**: Maximum object size: 5TB, no bucket size limit
- **CON-P2-005**: Must use existing Cloudflare setup (domain: esistwarm.jetzt)

### Security Requirements

- **SEC-P2-001**: Credentials stored only in environment variables / GitHub Secrets
- **SEC-P2-002**: No hardcoded credentials in any committed file
- **SEC-P2-003**: Public read access limited to `/tiles/` prefix only
- **SEC-P2-004**: Write access restricted to pipeline service accounts

### Guidelines

- **GUD-P2-001**: Follow existing S3 utility patterns (upload_to_s3.py, download_from_s3.py)
- **GUD-P2-002**: Validate environment variables at script startup
- **GUD-P2-003**: Use consistent naming conventions with existing infrastructure

### Patterns

- **PAT-P2-001**: Environment variable pattern: `ACCESS_KEY`, `SECRET_KEY`, `BUCKET_NAME`, `ENDPOINT_URL`, `REGION`
- **PAT-P2-002**: boto3 client initialization with `endpoint_url` parameter
- **PAT-P2-003**: CORS configuration via JSON file (infrastructure/bucket/)

## 2. Implementation Steps

### Implementation Phase 2.1: Hetzner Account & Bucket Setup

- GOAL-001: Create and configure Hetzner Object Storage bucket for ERA5-Land tiles

| Task     | Description                                                                                           | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-P2-001 | Create Hetzner Cloud account (if not existing) and enable Object Storage                             |           |      |
| TASK-P2-002 | Create bucket `climate-tiles` in fsn1 (Falkenstein) region via Hetzner Console                       |           |      |
| TASK-P2-003 | Generate Access Key and Secret Key for bucket access                                                 |           |      |
| TASK-P2-004 | Document bucket endpoint URL format: `https://climate-tiles.fsn1.your-objectstorage.com`             |           |      |
| TASK-P2-005 | Test bucket accessibility with boto3 (manual verification)                                           |           |      |

**Manual Steps for TASK-001 to TASK-004:**

```markdown
## Hetzner Object Storage Setup

1. Log in to Hetzner Cloud Console: https://console.hetzner.cloud/
2. Navigate to "Object Storage" in left sidebar
3. Click "Create Bucket"
   - Bucket name: `climate-tiles`
   - Location: fsn1 (Falkenstein, Germany)
4. After creation, click on bucket → "Keys" tab
5. Click "Create Key"
   - Description: "ERA5-Land Pipeline Access"
   - Copy Access Key and Secret Key immediately (shown only once)
6. Note the endpoint URL: `https://climate-tiles.fsn1.your-objectstorage.com`
```

---

### Implementation Phase 2.2: CORS Configuration

- GOAL-002: Configure CORS for browser-based tile loading

| Task     | Description                                                                                           | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-P2-006 | Create `infrastructure/bucket/era5-cors.json` with CORS rules                                        |           |      |
| TASK-P2-007 | Create `scripts/setup-hetzner-cors.sh` script to apply CORS configuration                            |           |      |
| TASK-P2-008 | Apply CORS configuration to bucket                                                                   |           |      |
| TASK-P2-009 | Verify CORS headers in browser DevTools                                                              |           |      |

---

### Implementation Phase 2.3: Upload Utility for Hetzner

- GOAL-003: Create/adapt S3 upload utility for Hetzner Object Storage

| Task     | Description                                                                                           | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-P2-010 | Verify/extend `analysis/utilities/upload_to_s3.py` - S3-compatible upload/download utilities                |           |      |
| TASK-P2-011 | Add content-type detection for WebP, JSON, and GeoTIFF files                                         |           |      |
| TASK-P2-012 | Add public-read ACL support for tile uploads                                                         |           |      |
| TASK-P2-013 | Add directory upload function for batch tile uploads                                                 |           |      |
| TASK-P2-014 | Write unit tests for upload utility with mocked boto3                                                |           |      |

---

### Implementation Phase 2.4: Environment Configuration

- GOAL-004: Establish environment variable schema and documentation

| Task     | Description                                                                                           | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-P2-015 | Create `.env.example` with all required environment variables                                        |           |      |
| TASK-P2-016 | Create `scripts/validate-env.py` - validate environment before pipeline runs                         |           |      |
| TASK-P2-017 | Document environment variables in `documentation/infrastructure/environment.md`                      |           |      |
| TASK-P2-018 | Add GitHub Secrets documentation for CI/CD setup                                                     |           |      |

---

### Implementation Phase 2.5: CDN Configuration (Cloudflare)

- GOAL-005: Configure Cloudflare caching for ERA5-Land tiles

| Task     | Description                                                                                           | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-P2-019 | Document Cloudflare cache rules for tile subdomain/path                                              |           |      |
| TASK-P2-020 | Create cache purge script for tile updates `scripts/purge-tile-cache.sh`                             |           |      |
| TASK-P2-021 | Test cache behavior with sample tile upload                                                          |           |      |

---

### Implementation Phase 2.6: Integration Testing

- GOAL-006: Verify complete infrastructure setup

| Task     | Description                                                                                           | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-P2-022 | Create `analysis/utilities/tests/test_upload_to_s3.py` - unit tests with mocked S3                |           |      |
| TASK-P2-023 | Create integration test script that uploads/downloads/deletes test file                              |           |      |
| TASK-P2-024 | Verify public URL accessibility for uploaded test tile                                               |           |      |
| TASK-P2-025 | Document infrastructure validation checklist                                                         |           |      |

## 3. Alternatives

- **ALT-001**: **Cloudflare R2 instead of Hetzner** - Considered due to integration with existing Cloudflare. Rejected because R2 charges €0.014/GB vs Hetzner €0.0052/GB, and project already uses Scaleway S3 successfully. Hetzner's free egress matches R2's free egress.

- **ALT-002**: **Scaleway Object Storage (current provider)** - Already in use for frontend assets. Considered using same bucket. Rejected to maintain separation between frontend hosting and data tiles - allows independent cost tracking and potential migration.

- **ALT-003**: **Single bucket for all data** - Rejected in favor of dedicated `climate-tiles` bucket for isolation, simpler CORS rules, and cleaner cost attribution. The name `climate-tiles` is intentionally dataset-agnostic to support future expansion beyond ERA5-Land.

- **ALT-004**: **Vercel Blob Storage** - Considered for frontend integration. Rejected due to higher costs and vendor lock-in. S3-compatible storage is more portable.

## 4. Dependencies

### External Dependencies

- **DEP-001**: Hetzner Cloud account with billing enabled
- **DEP-002**: Cloudflare account (existing: esistwarm.jetzt domain)
- **DEP-003**: GitHub repository secrets management (existing)

### Python Dependencies

- **DEP-004**: `boto3` - S3 client (existing in pyproject.toml)
- **DEP-005**: `python-dotenv` - Environment variable loading (for local development)
- **DEP-006**: `pytest` - Testing framework (existing)
- **DEP-007**: `pytest-mock` - Mocking for unit tests

### Phase Dependencies

- **DEP-008**: Phase 1 (Testing Infrastructure) should complete first for pytest setup
- **DEP-009**: No blocking dependencies - can run in parallel with Phase 1

## 5. Files

### Infrastructure Configuration Files

- **FILE-001**: `infrastructure/bucket/era5-cors.json` - NEW - CORS rules for ERA5-Land bucket
- **FILE-002**: `infrastructure/hetzner/README.md` - NEW - Hetzner setup documentation

### Script Files

- **FILE-003**: `scripts/setup-hetzner-cors.sh` - NEW - Apply CORS to Hetzner bucket
- **FILE-004**: `scripts/validate-env.py` - NEW - Environment validation script
- **FILE-005**: `scripts/purge-tile-cache.sh` - NEW - Cloudflare cache purge script
- **FILE-006**: `scripts/test-infrastructure.sh` - NEW - Infrastructure integration test

### Utility Files

- **FILE-007**: `analysis/utilities/upload_to_s3.py` - MODIFY - S3-compatible upload/download utilities (already exists; extend for ERA5-Land use)
- **FILE-008**: `analysis/utilities/tests/test_upload_to_s3.py` - NEW - Unit tests

### Configuration Files

- **FILE-009**: `.env.example` - NEW - Environment variable template
- **FILE-010**: `documentation/infrastructure/environment.md` - NEW - Environment documentation
- **FILE-011**: `documentation/infrastructure/hetzner-setup.md` - NEW - Hetzner setup guide

## 6. Testing

### Unit Tests

- **TEST-001**: `test_create_client()` - Verify boto3 client creation with Hetzner endpoint
- **TEST-002**: `test_upload_file()` - Verify file upload with correct content-type
- **TEST-003**: `test_upload_directory()` - Verify recursive directory upload
- **TEST-004**: `test_get_public_url()` - Verify public URL generation
- **TEST-005**: `test_content_type_detection()` - Verify WebP, JSON, GeoTIFF detection
- **TEST-006**: `test_validate_env()` - Verify environment validation catches missing vars

### Integration Tests (require credentials)

- **TEST-007**: Upload test WebP file and verify public accessibility
- **TEST-008**: Verify CORS headers present in response
- **TEST-009**: Upload/download roundtrip integrity check
- **TEST-010**: Verify cache headers from Cloudflare

### Mock Patterns

```python
# Pattern for mocking boto3 in unit tests
@pytest.fixture
def mock_s3_client(mocker):
    """Mock boto3 S3 client for unit tests."""
    mock_client = mocker.MagicMock()
    mocker.patch('boto3.client', return_value=mock_client)
    return mock_client

def test_upload_file(mock_s3_client):
    """Test file upload sets correct content-type."""
    from analysis.utilities.upload_to_s3 import upload_file
    
    upload_file('test.webp', 'tiles/test.webp')
    
    mock_s3_client.upload_file.assert_called_once()
    call_args = mock_s3_client.upload_file.call_args
    assert call_args.kwargs['ExtraArgs']['ContentType'] == 'image/webp'
```

## 7. Risks & Assumptions

### Risks

- **RISK-001**: Hetzner Object Storage API compatibility issues with boto3
  - **Mitigation**: Test with boto3 before committing to Hetzner; have fallback plan to Scaleway

- **RISK-002**: CORS configuration complexity with Hetzner
  - **Mitigation**: Hetzner supports standard S3 CORS API; use existing cors.json as template

- **RISK-003**: Cloudflare caching may serve stale tiles after updates
  - **Mitigation**: Include cache purge script; use versioned URLs if needed (e.g., `/tiles/v1/...`)

- **RISK-004**: Credential exposure in logs or error messages
  - **Mitigation**: Use environment variables only; add log filtering for sensitive patterns

### Assumptions

- **ASSUMPTION-001**: Hetzner Cloud account can be created and activated same-day
- **ASSUMPTION-002**: Hetzner Object Storage supports `put-bucket-cors` operation
- **ASSUMPTION-003**: boto3 works with Hetzner without modification (just endpoint change)
- **ASSUMPTION-004**: Existing Cloudflare setup can proxy to Hetzner origin or tiles served directly
- **ASSUMPTION-005**: Free egress applies to all bucket access patterns (CDN and direct)

## 8. Multi-Agent Execution Notes

### Execution Order

**Parallel tasks (can run simultaneously):**
- TASK-P2-006 and TASK-P2-015 (CORS config and .env.example creation)
- TASK-P2-010 to TASK-P2-014 (utility development) can parallel with TASK-P2-017-018 (documentation)

**Sequential dependencies:**
- TASK-P2-001 to TASK-P2-005 must complete first (bucket creation)
- TASK-P2-006 to TASK-P2-008 must complete before TASK-P2-009 (CORS verification)
- TASK-P2-010 to TASK-P2-013 must complete before TASK-P2-014 (tests need code)
- TASK-P2-022 to TASK-P2-025 require all prior tasks (integration testing)

### Agent Context Requirements

Executing agent needs:
- This plan document
- Existing patterns: `analysis/utilities/upload_to_s3.py`, `infrastructure/bucket/cors.json`
- Hetzner Object Storage documentation link
- Access to environment variables for integration testing

### Validation Checkpoints

- **After TASK-P2-005**: `boto3` can list bucket contents (empty list OK)
- **After TASK-P2-009**: Browser DevTools shows `Access-Control-Allow-Origin` header
- **After TASK-P2-014**: `pytest analysis/utilities/tests/test_upload_to_s3.py` passes
- **After TASK-P2-024**: Public URL returns 200 with test tile

## 9. Related Specifications / Further Reading

### Internal References
- [Master Plan](era5-germany-climate-visualization-1.md) - Overall architecture
- [Existing S3 Upload](../../analysis/utilities/upload_to_s3.py) - Reference pattern
- [Existing CORS Config](../../infrastructure/bucket/cors.json) - Reference pattern

### External Documentation
- [Hetzner Object Storage Docs](https://docs.hetzner.com/storage/object-storage/)
- [Hetzner S3 API Compatibility](https://docs.hetzner.com/storage/object-storage/overview#s3-api-compatibility)
- [boto3 S3 Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [Cloudflare Cache Rules](https://developers.cloudflare.com/cache/how-to/cache-rules/)

## 10. Code Reference (REQUIRED)

### 10.1 CORS Configuration for ERA5-Land Bucket

**File**: `infrastructure/bucket/era5-cors.json` - NEW

```json
{
    "CORSRules": [
        {
            "AllowedOrigins": [
                "https://esistwarm.jetzt",
                "https://*.esistwarm.jetzt",
                "http://localhost:3000",
                "http://localhost:5173"
            ],
            "AllowedHeaders": [
                "*"
            ],
            "AllowedMethods": [
                "GET",
                "HEAD"
            ],
            "MaxAgeSeconds": 86400,
            "ExposeHeaders": [
                "ETag",
                "Content-Length",
                "Content-Type",
                "Cache-Control"
            ]
        }
    ]
}
```

**Notes**: 
- `localhost:5173` is Vite's default dev server port
- `MaxAgeSeconds: 86400` (24 hours) reduces preflight requests
- Only GET/HEAD methods needed for tile serving

---

### 10.2 CORS Setup Script

**File**: `scripts/setup-hetzner-cors.sh` - NEW

```bash
#!/bin/bash
set -e

# Setup CORS for Hetzner Object Storage bucket
# Usage: ./scripts/setup-hetzner-cors.sh

# Configuration
BUCKET_NAME="${BUCKET_NAME:-climate-tiles}"
REGION="${REGION:-fsn1}"
ENDPOINT_URL="${ENDPOINT_URL:-https://${BUCKET_NAME}.${REGION}.your-objectstorage.com}"
CORS_FILE="infrastructure/bucket/era5-cors.json"

# Validate environment
if [ -z "$ACCESS_KEY" ] || [ -z "$SECRET_KEY" ]; then
    echo "Error: ACCESS_KEY and SECRET_KEY environment variables required."
    echo "Export them or use: ACCESS_KEY=xxx SECRET_KEY=yyy ./scripts/setup-hetzner-cors.sh"
    exit 1
fi

if [ ! -f "$CORS_FILE" ]; then
    echo "Error: CORS configuration file not found: $CORS_FILE"
    exit 1
fi

echo "Applying CORS configuration to bucket: $BUCKET_NAME"
echo "Endpoint: $ENDPOINT_URL"

# Apply CORS using AWS CLI with Hetzner endpoint
AWS_ACCESS_KEY_ID="$ACCESS_KEY" AWS_SECRET_ACCESS_KEY="$SECRET_KEY" \
    aws s3api put-bucket-cors \
    --bucket "$BUCKET_NAME" \
    --cors-configuration "file://$CORS_FILE" \
    --endpoint-url "$ENDPOINT_URL" \
    --region "$REGION"

echo "CORS configuration applied successfully."

# Verify CORS configuration
echo ""
echo "Verifying CORS configuration..."
AWS_ACCESS_KEY_ID="$ACCESS_KEY" AWS_SECRET_ACCESS_KEY="$SECRET_KEY" \
    aws s3api get-bucket-cors \
    --bucket "$BUCKET_NAME" \
    --endpoint-url "$ENDPOINT_URL" \
    --region "$REGION"

echo ""
echo "Done! CORS configuration is active."
```

**Notes**: Requires AWS CLI installed. Can also use boto3 directly (see 10.3).

---

### 10.3 S3 Storage Utility

**File**: `analysis/utilities/upload_to_s3.py` - MODIFY

```python
#!/usr/bin/env python3
"""
S3-compatible object storage utilities for ERA5-Land tile management.

This module provides upload/download functions that work with any
S3-compatible endpoint (Hetzner Object Storage, AWS S3, Cloudflare R2, etc.).

Usage:
    from analysis.utilities.upload_to_s3 import S3Storage
    
    storage = S3Storage()
    storage.upload_file('local/path/tile.webp', 'tiles/2025/01/6/32/21.webp')
    storage.upload_directory('local/tiles/', 'tiles/2025/01/')
"""

import os
import logging
import mimetypes
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Content type mappings for climate data files
CONTENT_TYPES = {
    '.webp': 'image/webp',
    '.json': 'application/json',
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.geotiff': 'image/tiff',
    '.nc': 'application/x-netcdf',
    '.csv': 'text/csv',
}


@dataclass
class S3Config:
    """Configuration for S3-compatible storage connection."""
    access_key: str
    secret_key: str
    bucket_name: str
    region: str = 'fsn1'
    endpoint_url: Optional[str] = None
    
    def __post_init__(self):
        if self.endpoint_url is None:
            self.endpoint_url = f'https://{self.bucket_name}.{self.region}.your-objectstorage.com'
    
    @classmethod
    def from_env(cls) -> 'S3Config':
        """Create config from environment variables."""
        required = ['ACCESS_KEY', 'SECRET_KEY', 'BUCKET_NAME']
        missing = [var for var in required if not os.environ.get(var)]
        
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        
        return cls(
            access_key=os.environ['ACCESS_KEY'],
            secret_key=os.environ['SECRET_KEY'],
            bucket_name=os.environ['BUCKET_NAME'],
            region=os.environ.get('REGION', 'fsn1'),
            endpoint_url=os.environ.get('ENDPOINT_URL'),
        )


class S3Storage:
    """Client for S3-compatible object storage operations."""
    
    def __init__(self, config: Optional[S3Config] = None):
        """Initialize storage client.
        
        Args:
            config: Storage configuration. If None, reads from environment.
        """
        self.config = config or S3Config.from_env()
        self._client: Optional[boto3.client] = None
    
    @property
    def client(self) -> boto3.client:
        """Lazy-initialized S3 client."""
        if self._client is None:
            self._client = boto3.client(
                's3',
                region_name=self.config.region,
                endpoint_url=self.config.endpoint_url,
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
            )
        return self._client
    
    def get_content_type(self, file_path: str) -> str:
        """Determine content type for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type string
        """
        ext = Path(file_path).suffix.lower()
        
        # Check custom mappings first
        if ext in CONTENT_TYPES:
            return CONTENT_TYPES[ext]
        
        # Fall back to mimetypes module
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'
    
    def upload_file(
        self,
        local_path: str,
        remote_key: str,
        public: bool = True,
        cache_control: Optional[str] = None,
    ) -> str:
        """Upload a single file to storage.
        
        Args:
            local_path: Path to local file
            remote_key: Object key in bucket (e.g., 'tiles/2025/01/6/32/21.webp')
            public: Whether to set public-read ACL
            cache_control: Optional Cache-Control header value
            
        Returns:
            Public URL of uploaded file
            
        Raises:
            FileNotFoundError: If local file doesn't exist
            ClientError: If upload fails
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"File not found: {local_path}")
        
        content_type = self.get_content_type(str(local_path))
        
        extra_args = {
            'ContentType': content_type,
        }
        
        if public:
            extra_args['ACL'] = 'public-read'
        
        if cache_control:
            extra_args['CacheControl'] = cache_control
        else:
            # Default cache control for static tiles
            extra_args['CacheControl'] = 'public, max-age=31536000'  # 1 year
        
        logger.info(f"Uploading {local_path} to {remote_key} (type: {content_type})")
        
        try:
            self.client.upload_file(
                str(local_path),
                self.config.bucket_name,
                remote_key,
                ExtraArgs=extra_args
            )
        except ClientError as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            raise
        
        return self.get_public_url(remote_key)
    
    def upload_directory(
        self,
        local_dir: str,
        remote_prefix: str,
        pattern: str = '*',
        public: bool = True,
    ) -> int:
        """Upload all files in a directory recursively.
        
        Args:
            local_dir: Local directory path
            remote_prefix: Prefix for all uploaded objects
            pattern: Glob pattern for files to include (default: all files)
            public: Whether to set public-read ACL
            
        Returns:
            Number of files uploaded
        """
        local_dir = Path(local_dir)
        if not local_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {local_dir}")
        
        # Normalize remote prefix
        remote_prefix = remote_prefix.strip('/')
        if remote_prefix:
            remote_prefix += '/'
        
        uploaded = 0
        for local_path in local_dir.rglob(pattern):
            if local_path.is_file():
                relative = local_path.relative_to(local_dir)
                remote_key = f"{remote_prefix}{relative}"
                self.upload_file(str(local_path), remote_key, public=public)
                uploaded += 1
        
        logger.info(f"Uploaded {uploaded} files to {remote_prefix}")
        return uploaded
    
    def get_public_url(self, remote_key: str) -> str:
        """Get public URL for an object.
        
        Args:
            remote_key: Object key in bucket
            
        Returns:
            Public HTTPS URL
        """
        # Hetzner URL format: https://<bucket>.<region>.your-objectstorage.com/<key>
        return f"{self.config.endpoint_url}/{remote_key}"
    
    def download_file(self, remote_key: str, local_path: str) -> Path:
        """Download a file from storage.
        
        Args:
            remote_key: Object key in bucket
            local_path: Local destination path
            
        Returns:
            Path to downloaded file
        """
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Downloading {remote_key} to {local_path}")
        
        try:
            self.client.download_file(
                self.config.bucket_name,
                remote_key,
                str(local_path)
            )
        except ClientError as e:
            logger.error(f"Failed to download {remote_key}: {e}")
            raise
        
        return local_path
    
    def delete_file(self, remote_key: str) -> None:
        """Delete a file from storage.
        
        Args:
            remote_key: Object key in bucket
        """
        logger.info(f"Deleting {remote_key}")
        
        try:
            self.client.delete_object(
                Bucket=self.config.bucket_name,
                Key=remote_key
            )
        except ClientError as e:
            logger.error(f"Failed to delete {remote_key}: {e}")
            raise
    
    def file_exists(self, remote_key: str) -> bool:
        """Check if a file exists in storage.
        
        Args:
            remote_key: Object key in bucket
            
        Returns:
            True if file exists
        """
        try:
            self.client.head_object(
                Bucket=self.config.bucket_name,
                Key=remote_key
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
    
    def list_files(self, prefix: str = '', max_keys: int = 1000) -> list[str]:
        """List files in storage with given prefix.
        
        Args:
            prefix: Key prefix to filter by
            max_keys: Maximum number of keys to return
            
        Returns:
            List of object keys
        """
        paginator = self.client.get_paginator('list_objects_v2')
        keys = []
        
        for page in paginator.paginate(
            Bucket=self.config.bucket_name,
            Prefix=prefix,
            PaginationConfig={'MaxItems': max_keys}
        ):
            if 'Contents' in page:
                keys.extend(obj['Key'] for obj in page['Contents'])
        
        return keys
    
    def set_cors(self, cors_config: dict) -> None:
        """Set CORS configuration for the bucket.
        
        Args:
            cors_config: CORS configuration dictionary
        """
        logger.info(f"Setting CORS configuration for {self.config.bucket_name}")
        
        try:
            self.client.put_bucket_cors(
                Bucket=self.config.bucket_name,
                CORSConfiguration=cors_config
            )
        except ClientError as e:
            logger.error(f"Failed to set CORS: {e}")
            raise
    
    def get_cors(self) -> dict:
        """Get current CORS configuration.
        
        Returns:
            CORS configuration dictionary
        """
        try:
            response = self.client.get_bucket_cors(Bucket=self.config.bucket_name)
            return response.get('CORSRules', [])
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchCORSConfiguration':
                return []
            raise


# Convenience functions for CLI usage
def upload_file(local_path: str, remote_key: str, public: bool = True) -> str:
    """Upload a single file (convenience function)."""
    storage = HetznerStorage()
    return storage.upload_file(local_path, remote_key, public)


def upload_directory(local_dir: str, remote_prefix: str, public: bool = True) -> int:
    """Upload a directory (convenience function)."""
    storage = HetznerStorage()
    return storage.upload_directory(local_dir, remote_prefix, public=public)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Hetzner Object Storage utility')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload file or directory')
    upload_parser.add_argument('local_path', help='Local file or directory path')
    upload_parser.add_argument('remote_key', help='Remote key or prefix')
    upload_parser.add_argument('--private', action='store_true', help='Do not set public-read ACL')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download file')
    download_parser.add_argument('remote_key', help='Remote key')
    download_parser.add_argument('local_path', help='Local destination path')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List files')
    list_parser.add_argument('--prefix', default='', help='Filter by prefix')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete file')
    delete_parser.add_argument('remote_key', help='Remote key to delete')
    
    args = parser.parse_args()
    storage = HetznerStorage()
    
    if args.command == 'upload':
        path = Path(args.local_path)
        if path.is_dir():
            count = storage.upload_directory(args.local_path, args.remote_key, public=not args.private)
            print(f"Uploaded {count} files")
        else:
            url = storage.upload_file(args.local_path, args.remote_key, public=not args.private)
            print(f"Uploaded to: {url}")
    
    elif args.command == 'download':
        storage.download_file(args.remote_key, args.local_path)
        print(f"Downloaded to: {args.local_path}")
    
    elif args.command == 'list':
        files = storage.list_files(args.prefix)
        for f in files:
            print(f)
    
    elif args.command == 'delete':
        storage.delete_file(args.remote_key)
        print(f"Deleted: {args.remote_key}")
```

**Notes**:
- Uses lazy initialization for boto3 client
- Content-type detection for WebP tiles
- Default cache-control of 1 year for immutable tiles
- CLI interface for manual operations
- Compatible with existing `upload_to_s3.py` patterns

---

### 10.4 Unit Tests for Storage Utility

**File**: `analysis/utilities/tests/test_upload_to_s3.py` - NEW

```python
#!/usr/bin/env python3
"""Unit tests for S3-compatible storage utility."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from analysis.utilities.upload_to_s3 import (
    S3Storage,
    S3Config,
    CONTENT_TYPES,
)


@pytest.fixture
def mock_config():
    """Create test configuration."""
    return S3Config(
        access_key='test-access-key',
        secret_key='test-secret-key',
        bucket_name='test-bucket',
        region='fsn1',
    )


@pytest.fixture
def mock_s3_client(mocker):
    """Mock boto3 S3 client."""
    mock_client = MagicMock()
    mocker.patch('boto3.client', return_value=mock_client)
    return mock_client


@pytest.fixture
def storage(mock_config, mock_s3_client):
    """Create storage instance with mocked client."""
    return S3Storage(config=mock_config)


class TestS3Config:
    """Tests for S3Config."""
    
    def test_endpoint_url_generated(self):
        """Test endpoint URL is generated from bucket and region."""
        config = S3Config(
            access_key='key',
            secret_key='secret',
            bucket_name='my-bucket',
            region='fsn1',
        )
        assert config.endpoint_url == 'https://my-bucket.fsn1.your-objectstorage.com'
    
    def test_custom_endpoint_url(self):
        """Test custom endpoint URL is preserved."""
        config = S3Config(
            access_key='key',
            secret_key='secret',
            bucket_name='my-bucket',
            endpoint_url='https://custom.endpoint.com',
        )
        assert config.endpoint_url == 'https://custom.endpoint.com'
    
    def test_from_env_missing_vars(self, mocker):
        """Test error when environment variables are missing."""
        mocker.patch.dict('os.environ', {}, clear=True)
        
        with pytest.raises(EnvironmentError) as exc_info:
            S3Config.from_env()
        
        assert 'ACCESS_KEY' in str(exc_info.value)
    
    def test_from_env_success(self, mocker):
        """Test successful config creation from environment."""
        mocker.patch.dict('os.environ', {
            'ACCESS_KEY': 'env-key',
            'SECRET_KEY': 'env-secret',
            'BUCKET_NAME': 'env-bucket',
            'REGION': 'hel1',
        })
        
        config = S3Config.from_env()
        
        assert config.access_key == 'env-key'
        assert config.secret_key == 'env-secret'
        assert config.bucket_name == 'env-bucket'
        assert config.region == 'hel1'


class TestContentTypeDetection:
    """Tests for content type detection."""
    
    def test_webp_content_type(self, storage):
        """Test WebP files get correct content type."""
        assert storage.get_content_type('tile.webp') == 'image/webp'
        assert storage.get_content_type('/path/to/tile.WEBP') == 'image/webp'
    
    def test_json_content_type(self, storage):
        """Test JSON files get correct content type."""
        assert storage.get_content_type('metrics.json') == 'application/json'
    
    def test_tiff_content_type(self, storage):
        """Test TIFF/GeoTIFF files get correct content type."""
        assert storage.get_content_type('data.tif') == 'image/tiff'
        assert storage.get_content_type('data.tiff') == 'image/tiff'
        assert storage.get_content_type('data.geotiff') == 'image/tiff'
    
    def test_netcdf_content_type(self, storage):
        """Test NetCDF files get correct content type."""
        assert storage.get_content_type('data.nc') == 'application/x-netcdf'
    
    def test_unknown_fallback(self, storage):
        """Test unknown extensions fall back to octet-stream."""
        assert storage.get_content_type('data.xyz') == 'application/octet-stream'


class TestUploadFile:
    """Tests for file upload functionality."""
    
    def test_upload_with_correct_content_type(self, storage, mock_s3_client, tmp_path):
        """Test upload sets correct content type."""
        test_file = tmp_path / 'test.webp'
        test_file.write_bytes(b'fake webp content')
        
        storage.upload_file(str(test_file), 'tiles/test.webp')
        
        mock_s3_client.upload_file.assert_called_once()
        call_args = mock_s3_client.upload_file.call_args
        assert call_args.kwargs['ExtraArgs']['ContentType'] == 'image/webp'
    
    def test_upload_public_acl(self, storage, mock_s3_client, tmp_path):
        """Test upload sets public-read ACL by default."""
        test_file = tmp_path / 'test.webp'
        test_file.write_bytes(b'content')
        
        storage.upload_file(str(test_file), 'tiles/test.webp')
        
        call_args = mock_s3_client.upload_file.call_args
        assert call_args.kwargs['ExtraArgs']['ACL'] == 'public-read'
    
    def test_upload_private(self, storage, mock_s3_client, tmp_path):
        """Test upload without public ACL."""
        test_file = tmp_path / 'test.webp'
        test_file.write_bytes(b'content')
        
        storage.upload_file(str(test_file), 'tiles/test.webp', public=False)
        
        call_args = mock_s3_client.upload_file.call_args
        assert 'ACL' not in call_args.kwargs['ExtraArgs']
    
    def test_upload_cache_control(self, storage, mock_s3_client, tmp_path):
        """Test upload sets cache-control header."""
        test_file = tmp_path / 'test.webp'
        test_file.write_bytes(b'content')
        
        storage.upload_file(str(test_file), 'tiles/test.webp')
        
        call_args = mock_s3_client.upload_file.call_args
        assert 'max-age=31536000' in call_args.kwargs['ExtraArgs']['CacheControl']
    
    def test_upload_file_not_found(self, storage):
        """Test upload raises error for missing file."""
        with pytest.raises(FileNotFoundError):
            storage.upload_file('/nonexistent/file.webp', 'key')
    
    def test_upload_returns_public_url(self, storage, mock_s3_client, tmp_path):
        """Test upload returns correct public URL."""
        test_file = tmp_path / 'test.webp'
        test_file.write_bytes(b'content')
        
        url = storage.upload_file(str(test_file), 'tiles/2025/01/6/32/21.webp')
        
        assert url == 'https://test-bucket.fsn1.your-objectstorage.com/tiles/2025/01/6/32/21.webp'


class TestUploadDirectory:
    """Tests for directory upload functionality."""
    
    def test_upload_directory_recursive(self, storage, mock_s3_client, tmp_path):
        """Test directory upload is recursive."""
        # Create directory structure
        (tmp_path / 'a').mkdir()
        (tmp_path / 'a' / 'b').mkdir()
        (tmp_path / 'file1.webp').write_bytes(b'1')
        (tmp_path / 'a' / 'file2.webp').write_bytes(b'2')
        (tmp_path / 'a' / 'b' / 'file3.webp').write_bytes(b'3')
        
        count = storage.upload_directory(str(tmp_path), 'tiles/')
        
        assert count == 3
        assert mock_s3_client.upload_file.call_count == 3
    
    def test_upload_directory_preserves_structure(self, storage, mock_s3_client, tmp_path):
        """Test directory upload preserves directory structure."""
        (tmp_path / 'sub').mkdir()
        (tmp_path / 'root.webp').write_bytes(b'root')
        (tmp_path / 'sub' / 'nested.webp').write_bytes(b'nested')
        
        storage.upload_directory(str(tmp_path), 'prefix/')
        
        uploaded_keys = [call.args[2] for call in mock_s3_client.upload_file.call_args_list]
        assert 'prefix/root.webp' in uploaded_keys
        assert 'prefix/sub/nested.webp' in uploaded_keys
    
    def test_upload_directory_not_dir(self, storage, tmp_path):
        """Test error when path is not a directory."""
        test_file = tmp_path / 'file.txt'
        test_file.write_text('content')
        
        with pytest.raises(NotADirectoryError):
            storage.upload_directory(str(test_file), 'prefix/')


class TestPublicUrl:
    """Tests for public URL generation."""
    
    def test_get_public_url(self, storage):
        """Test public URL format."""
        url = storage.get_public_url('tiles/2025/01/6/32/21.webp')
        assert url == 'https://test-bucket.fsn1.your-objectstorage.com/tiles/2025/01/6/32/21.webp'


class TestFileExists:
    """Tests for file existence check."""
    
    def test_file_exists_true(self, storage, mock_s3_client):
        """Test file exists returns True when file is present."""
        mock_s3_client.head_object.return_value = {}
        
        assert storage.file_exists('test/key') is True
    
    def test_file_exists_false(self, storage, mock_s3_client):
        """Test file exists returns False for 404."""
        error_response = {'Error': {'Code': '404'}}
        mock_s3_client.head_object.side_effect = ClientError(error_response, 'HeadObject')
        
        assert storage.file_exists('missing/key') is False


class TestCors:
    """Tests for CORS operations."""
    
    def test_set_cors(self, storage, mock_s3_client):
        """Test setting CORS configuration."""
        cors_config = {'CORSRules': [{'AllowedOrigins': ['*']}]}
        
        storage.set_cors(cors_config)
        
        mock_s3_client.put_bucket_cors.assert_called_once_with(
            Bucket='test-bucket',
            CORSConfiguration=cors_config
        )
    
    def test_get_cors(self, storage, mock_s3_client):
        """Test getting CORS configuration."""
        mock_s3_client.get_bucket_cors.return_value = {
            'CORSRules': [{'AllowedOrigins': ['https://example.com']}]
        }
        
        rules = storage.get_cors()
        
        assert len(rules) == 1
        assert rules[0]['AllowedOrigins'] == ['https://example.com']
    
    def test_get_cors_no_config(self, storage, mock_s3_client):
        """Test getting CORS when none configured."""
        error_response = {'Error': {'Code': 'NoSuchCORSConfiguration'}}
        mock_s3_client.get_bucket_cors.side_effect = ClientError(
            error_response, 'GetBucketCors'
        )
        
        rules = storage.get_cors()
        
        assert rules == []
```

**Notes**:
- Uses pytest-mock for clean mocking
- Tests content-type detection for all climate data formats
- Tests public vs private uploads
- Tests error handling for missing files

---

### 10.5 Environment Variable Template

**File**: `.env.example` - NEW

```bash
# ERA5-Land Climate Visualization - Environment Variables
# Copy this file to .env and fill in your values
# NEVER commit .env to version control!

# =============================================================================
# Hetzner Object Storage (ERA5-Land tiles)
# =============================================================================

# S3-compatible access key (Hetzner Object Storage → Keys)
S3_ACCESS_KEY=your_access_key_here

# S3-compatible secret key (Hetzner Object Storage → Keys)
S3_SECRET_KEY=your_secret_key_here

# Bucket name (must match bucket created in Hetzner console)
S3_BUCKET_NAME=climate-tiles

# Region (fsn1 = Falkenstein, nbg1 = Nuremberg, hel1 = Helsinki)
S3_REGION=fsn1

# Endpoint URL (optional - auto-generated from bucket and region if not set)
# S3_ENDPOINT_URL=https://climate-tiles.fsn1.your-objectstorage.com

# =============================================================================
# Scaleway Object Storage (Frontend hosting - existing)
# =============================================================================

# Scaleway access key (existing)
ACCESS_KEY=your_scaleway_access_key

# Scaleway secret key (existing)
SECRET_KEY=your_scaleway_secret_key

# Scaleway bucket name (existing)
BUCKET_NAME=esistwarm.jetzt

# Scaleway region
REGION=fr-par

# Scaleway endpoint
ENDPOINT_URL=https://s3.fr-par.scw.cloud

# =============================================================================
# Copernicus Climate Data Store (ERA5-Land data)
# =============================================================================

# CDS API key (from https://cds.climate.copernicus.eu/user)
CDS_API_KEY=your_cds_api_key_here

# CDS API URL (usually doesn't need changing)
CDS_API_URL=https://cds.climate.copernicus.eu/api/v2

# =============================================================================
# Frontend Development
# =============================================================================

# Base URL for ERA5-Land tiles (for frontend development)
VITE_TILE_BASE_URL=https://climate-tiles.fsn1.your-objectstorage.com

# Enable development mode features
VITE_DEV_MODE=true

# =============================================================================
# CI/CD (GitHub Actions)
# =============================================================================
# These are set as GitHub Secrets, not in .env
# - S3_ACCESS_KEY
# - S3_SECRET_KEY
# - CDS_API_KEY
# - AWS_ACCESS_KEY_ID (Scaleway)
# - AWS_SECRET_ACCESS_KEY (Scaleway)
```

**Notes**:
- Clear separation between Hetzner (ERA5-Land) and Scaleway (frontend)
- Includes all variables needed for Phase 3+ pipelines
- Documents GitHub Secrets for CI/CD

---

### 10.6 Environment Validation Script

**File**: `scripts/validate-env.py` - NEW

```python
#!/usr/bin/env python3
"""
Validate environment variables before running pipelines.

Usage:
    python scripts/validate-env.py              # Validate all
    python scripts/validate-env.py --hetzner    # Validate Hetzner only
    python scripts/validate-env.py --cds        # Validate CDS only
"""

import os
import sys
import argparse
from dataclasses import dataclass
from typing import Optional

# Try to load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class EnvVar:
    """Environment variable definition."""
    name: str
    required: bool = True
    description: str = ''
    example: str = ''


# Environment variable groups
S3_VARS = [
    EnvVar('S3_ACCESS_KEY', True, 'S3-compatible access key'),
    EnvVar('S3_SECRET_KEY', True, 'S3-compatible secret key'),
    EnvVar('S3_BUCKET_NAME', True, 'Bucket name', 'climate-tiles'),
    EnvVar('S3_REGION', False, 'Region', 'fsn1'),
    EnvVar('S3_ENDPOINT_URL', False, 'Endpoint URL (auto-generated if not set)'),
]

# Legacy env var names (for backwards compatibility)
LEGACY_S3_VARS = [
    EnvVar('ACCESS_KEY', True, 'S3 access key (legacy)'),
    EnvVar('SECRET_KEY', True, 'S3 secret key (legacy)'),
    EnvVar('BUCKET_NAME', True, 'Bucket name (legacy)'),
    EnvVar('REGION', False, 'Region (legacy)'),
    EnvVar('ENDPOINT_URL', False, 'Endpoint URL (legacy)'),
]

CDS_VARS = [
    EnvVar('CDS_API_KEY', True, 'Copernicus CDS API key'),
    EnvVar('CDS_API_URL', False, 'CDS API URL', 'https://cds.climate.copernicus.eu/api/v2'),
]

SCALEWAY_VARS = [
    EnvVar('ACCESS_KEY', True, 'Scaleway access key'),
    EnvVar('SECRET_KEY', True, 'Scaleway secret key'),
    EnvVar('BUCKET_NAME', True, 'Scaleway bucket name'),
    EnvVar('REGION', True, 'Scaleway region', 'fr-par'),
    EnvVar('ENDPOINT_URL', True, 'Scaleway endpoint URL'),
]


def validate_group(vars: list[EnvVar], group_name: str, use_legacy: bool = False) -> tuple[bool, list[str]]:
    """Validate a group of environment variables.
    
    Args:
        vars: List of EnvVar definitions
        group_name: Name of the group for error messages
        use_legacy: Whether to try legacy variable names as fallback
        
    Returns:
        Tuple of (all_valid, list_of_errors)
    """
    errors = []
    
    for var in vars:
        value = os.environ.get(var.name)
        
        if not value and var.required:
            # Check legacy fallback
            legacy_name = var.name.replace('S3_', '')
            legacy_value = os.environ.get(legacy_name) if use_legacy else None
            
            if legacy_value:
                print(f"  ⚠️  {var.name}: Using legacy {legacy_name}")
            else:
                errors.append(f"{var.name}: Required but not set")
                if var.example:
                    errors[-1] += f" (example: {var.example})"
        elif value:
            # Mask the value for security
            masked = value[:4] + '****' if len(value) > 4 else '****'
            print(f"  ✓  {var.name}: {masked}")
        else:
            print(f"  -  {var.name}: Not set (optional)")
    
    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(description='Validate environment variables')
    parser.add_argument('--hetzner', action='store_true', help='Validate Hetzner vars only')
    parser.add_argument('--cds', action='store_true', help='Validate CDS vars only')
    parser.add_argument('--scaleway', action='store_true', help='Validate Scaleway vars only')
    parser.add_argument('--legacy', action='store_true', help='Accept legacy variable names')
    parser.add_argument('--quiet', action='store_true', help='Only show errors')
    args = parser.parse_args()
    
    # If no specific group selected, validate all
    validate_all = not (args.hetzner or args.cds or args.scaleway)
    
    all_valid = True
    all_errors = []
    
    if args.hetzner or validate_all:
        print("\n🔐 Hetzner Object Storage:")
        valid, errors = validate_group(
            S3_VARS if not args.legacy else LEGACY_S3_VARS,
            "S3 Storage",
            use_legacy=args.legacy
        )
        all_valid = all_valid and valid
        all_errors.extend(errors)
    
    if args.cds or validate_all:
        print("\n🌍 Copernicus CDS:")
        valid, errors = validate_group(CDS_VARS, "CDS")
        all_valid = all_valid and valid
        all_errors.extend(errors)
    
    if args.scaleway or validate_all:
        print("\n☁️  Scaleway (Frontend):")
        valid, errors = validate_group(SCALEWAY_VARS, "Scaleway")
        all_valid = all_valid and valid
        all_errors.extend(errors)
    
    # Summary
    print("\n" + "=" * 50)
    if all_valid:
        print("✅ All required environment variables are set!")
        sys.exit(0)
    else:
        print("❌ Missing required environment variables:")
        for error in all_errors:
            print(f"   - {error}")
        print("\nSee .env.example for required variables.")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

**Notes**:
- Groups variables by service
- Masks sensitive values in output
- Supports both new (S3_*) and legacy (ACCESS_KEY) naming
- Exit code indicates validation result for CI integration

---

### 10.7 Cache Purge Script

**File**: `scripts/purge-tile-cache.sh` - NEW

```bash
#!/bin/bash
set -e

# Purge Cloudflare cache for ERA5-Land tiles
# Usage: ./scripts/purge-tile-cache.sh [path_prefix]
#
# Examples:
#   ./scripts/purge-tile-cache.sh                    # Purge all tiles
#   ./scripts/purge-tile-cache.sh tiles/2025/01/     # Purge January 2025 only

# Configuration
CLOUDFLARE_ZONE_ID="${CLOUDFLARE_ZONE_ID:-}"
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-}"
TILE_BASE_URL="${VITE_TILE_BASE_URL:-https://climate-tiles.fsn1.your-objectstorage.com}"

# Validate configuration
if [ -z "$CLOUDFLARE_ZONE_ID" ] || [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "Error: CLOUDFLARE_ZONE_ID and CLOUDFLARE_API_TOKEN must be set."
    echo "Get these from Cloudflare dashboard → Zone → API section"
    exit 1
fi

# Path prefix (optional argument)
PATH_PREFIX="${1:-tiles/}"

echo "Purging Cloudflare cache..."
echo "Zone ID: $CLOUDFLARE_ZONE_ID"
echo "URL pattern: ${TILE_BASE_URL}/${PATH_PREFIX}*"

# Purge by prefix (requires Cloudflare Pro or higher)
# For free tier, use purge everything or specific URLs

# Option 1: Purge everything (works on free tier but aggressive)
# curl -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/purge_cache" \
#      -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
#      -H "Content-Type: application/json" \
#      --data '{"purge_everything":true}'

# Option 2: Purge by URLs (up to 30 URLs per request, works on free tier)
# Construct URLs to purge
URLS_TO_PURGE="[\"${TILE_BASE_URL}/${PATH_PREFIX}\"]"

curl -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/purge_cache" \
     -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
     -H "Content-Type: application/json" \
     --data "{\"files\":${URLS_TO_PURGE}}"

echo ""
echo "Cache purge request sent."
echo "Note: It may take up to 30 seconds for the cache to clear globally."
```

**Notes**:
- Works with Cloudflare free tier (limited to specific URLs)
- For bulk purges, consider Cloudflare Pro or time-based cache invalidation
- Alternatively, use versioned URLs (e.g., `/tiles/v1/...`) to avoid cache issues

---

### 10.8 Infrastructure Test Script

**File**: `scripts/test-infrastructure.sh` - NEW

```bash
#!/bin/bash
set -e

# Integration test for ERA5-Land infrastructure
# Tests: bucket access, upload, download, public URL, CORS
#
# Usage: ./scripts/test-infrastructure.sh
#
# Requires: ACCESS_KEY, SECRET_KEY, BUCKET_NAME, REGION, ENDPOINT_URL

echo "🧪 ERA5-Land Infrastructure Integration Test"
echo "========================================"

# Validate environment
if [ -z "$ACCESS_KEY" ] || [ -z "$SECRET_KEY" ] || [ -z "$BUCKET_NAME" ]; then
    echo "❌ Error: Missing environment variables."
    echo "Required: ACCESS_KEY, SECRET_KEY, BUCKET_NAME"
    echo "Optional: REGION (default: fsn1), ENDPOINT_URL"
    exit 1
fi

REGION="${REGION:-fsn1}"
ENDPOINT_URL="${ENDPOINT_URL:-https://${BUCKET_NAME}.${REGION}.your-objectstorage.com}"

echo "Bucket: $BUCKET_NAME"
echo "Region: $REGION"
echo "Endpoint: $ENDPOINT_URL"
echo ""

# Create test file
TEST_DIR=$(mktemp -d)
TEST_FILE="$TEST_DIR/test-tile.webp"
TEST_KEY="__test__/test-tile-$(date +%s).webp"

# Create a minimal WebP file (1x1 transparent pixel)
# This is a valid WebP file header
echo -n "RIFF" > "$TEST_FILE"
printf '\x1a\x00\x00\x00' >> "$TEST_FILE"
echo -n "WEBPVP8 " >> "$TEST_FILE"
printf '\x0d\x00\x00\x00\x30\x01\x00\x9d\x01\x2a\x01\x00\x01\x00\x00\x34\x25\x9f' >> "$TEST_FILE"

echo "📤 Test 1: Upload file..."
python -c "
from analysis.utilities.upload_to_s3 import S3Storage
storage = S3Storage()
url = storage.upload_file('$TEST_FILE', '$TEST_KEY')
print(f'Uploaded to: {url}')
"

PUBLIC_URL="${ENDPOINT_URL}/${TEST_KEY}"

echo ""
echo "🔍 Test 2: Verify public URL accessibility..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PUBLIC_URL")
if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "✅ Public URL accessible (HTTP $HTTP_STATUS)"
else
    echo "❌ Public URL not accessible (HTTP $HTTP_STATUS)"
    echo "URL: $PUBLIC_URL"
fi

echo ""
echo "🔍 Test 3: Check content-type header..."
CONTENT_TYPE=$(curl -s -I "$PUBLIC_URL" | grep -i "content-type" | cut -d' ' -f2 | tr -d '\r')
if [ "$CONTENT_TYPE" = "image/webp" ]; then
    echo "✅ Content-Type is correct: $CONTENT_TYPE"
else
    echo "⚠️  Content-Type: $CONTENT_TYPE (expected: image/webp)"
fi

echo ""
echo "🔍 Test 4: Check CORS headers..."
CORS_HEADER=$(curl -s -I -H "Origin: https://esistwarm.jetzt" "$PUBLIC_URL" | grep -i "access-control-allow-origin" || echo "")
if [ -n "$CORS_HEADER" ]; then
    echo "✅ CORS headers present: $CORS_HEADER"
else
    echo "⚠️  CORS headers not found (may need to configure CORS)"
fi

echo ""
echo "📥 Test 5: Download file..."
DOWNLOAD_PATH="$TEST_DIR/downloaded.webp"
python -c "
from analysis.utilities.upload_to_s3 import S3Storage
storage = S3Storage()
storage.download_file('$TEST_KEY', '$DOWNLOAD_PATH')
print('Downloaded successfully')
"

echo ""
echo "🗑️  Test 6: Cleanup test file..."
python -c "
from analysis.utilities.upload_to_s3 import S3Storage
storage = S3Storage()
storage.delete_file('$TEST_KEY')
print('Deleted test file')
"

# Verify deletion
sleep 1
HTTP_STATUS_AFTER=$(curl -s -o /dev/null -w "%{http_code}" "$PUBLIC_URL")
if [ "$HTTP_STATUS_AFTER" -eq 404 ] || [ "$HTTP_STATUS_AFTER" -eq 403 ]; then
    echo "✅ File deleted successfully"
else
    echo "⚠️  File may still be cached (HTTP $HTTP_STATUS_AFTER)"
fi

# Cleanup
rm -rf "$TEST_DIR"

echo ""
echo "========================================"
echo "✅ Infrastructure test complete!"
```

**Notes**:
- Creates minimal valid WebP file for testing
- Tests upload, public access, content-type, CORS, download, and delete
- Can be run manually or in CI after infrastructure setup

---

### 10.9 Documentation: Hetzner Setup Guide

**File**: `documentation/infrastructure/hetzner-setup.md` - NEW

```markdown
# Hetzner Object Storage Setup Guide

This guide covers setting up Hetzner Object Storage for ERA5-Land climate visualization tiles.

## Prerequisites

- Hetzner Cloud account (create at https://console.hetzner.cloud/)
- Payment method added to account
- AWS CLI or Python with boto3 installed

## 1. Create Bucket

1. Log in to [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Navigate to **Object Storage** in the left sidebar
3. Click **Create Bucket**
4. Configure:
   - **Bucket name**: `climate-tiles`
   - **Location**: `fsn1` (Falkenstein, Germany) - closest to most German users
5. Click **Create**

## 2. Generate Access Keys

1. Click on your new bucket → **Keys** tab
2. Click **Create Key**
3. Set description: "ERA5-Land Pipeline Access"
4. **Copy the Access Key and Secret Key immediately** (shown only once!)
5. Store securely (password manager or environment variables)

## 3. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```bash
S3_ACCESS_KEY=your_access_key_here
S3_SECRET_KEY=your_secret_key_here
S3_BUCKET_NAME=climate-tiles
S3_REGION=fsn1
```

## 4. Apply CORS Configuration

Run the CORS setup script:

```bash
source .env  # Load environment variables
./scripts/setup-hetzner-cors.sh
```

This applies the CORS rules from `infrastructure/bucket/era5-cors.json`.

## 5. Verify Setup

Run the integration test:

```bash
source .env
./scripts/test-infrastructure.sh
```

Expected output:
- ✅ Upload successful
- ✅ Public URL accessible
- ✅ Content-Type correct
- ✅ CORS headers present
- ✅ Download successful
- ✅ Delete successful

## Endpoints

| Region | Location | Endpoint URL |
|--------|----------|--------------|
| fsn1 | Falkenstein, Germany | `https://climate-tiles.fsn1.your-objectstorage.com` |
| nbg1 | Nuremberg, Germany | `https://climate-tiles.nbg1.your-objectstorage.com` |
| hel1 | Helsinki, Finland | `https://climate-tiles.hel1.your-objectstorage.com` |

## Pricing (as of 2026)

| Item | Price |
|------|-------|
| Storage | €0.0052/GB/month |
| Egress | Free (included) |
| Requests | Free (included) |

For ERA5-Land tiles (~500MB estimated), monthly cost is approximately €0.003/month.

## Troubleshooting

### "Access Denied" errors

- Verify ACCESS_KEY and SECRET_KEY are correct
- Check if bucket exists and is in the correct region
- Ensure endpoint URL matches bucket region

### CORS not working

- Verify CORS configuration was applied: `./scripts/setup-hetzner-cors.sh`
- Check browser console for specific CORS error messages
- Confirm `AllowedOrigins` includes your development URL

### Files not publicly accessible

- Ensure uploads use `ACL='public-read'`
- Verify bucket permissions in Hetzner console

## Security Notes

- Never commit credentials to version control
- Use environment variables or secrets management
- Rotate keys periodically
- Consider using separate keys for CI/CD vs manual operations
```

**Notes**: This documentation ensures reproducible setup for new team members or disaster recovery.

---

### 10.10 GitHub Actions Secret Configuration

**Reference for Phase 5 - GitHub Actions setup**

```yaml
# Secrets to add in GitHub repository settings:
# Settings → Secrets and variables → Actions → New repository secret

# ERA5-Land Tiles (S3-compatible / Hetzner Object Storage):
S3_ACCESS_KEY: <from-hetzner-console>
S3_SECRET_KEY: <from-hetzner-console>
S3_BUCKET_NAME: climate-tiles
S3_REGION: fsn1

# Copernicus CDS (for ERA5-Land downloads):
CDS_API_KEY: <from-cds-profile>

# Scaleway (existing, for frontend):
AWS_ACCESS_KEY_ID: <existing>
AWS_SECRET_ACCESS_KEY: <existing>
S3_ENDPOINT_URL: <existing>
S3_BUCKET_NAME: <existing>

# Cloudflare (for cache purging):
CLOUDFLARE_ZONE_ID: <from-cloudflare-dashboard>
CLOUDFLARE_API_TOKEN: <from-cloudflare-api-tokens>
```

**Notes**: Document for reference when setting up GitHub Actions in Phase 5.
