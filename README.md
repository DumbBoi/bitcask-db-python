### On Disk Key Vlaue DB

## Overview

Simple on disk key/value store implemented in Python. The project exposes a grpc service (server implemented in [src/main.py](src/main.py)) that delegates storage to the database implementation in [src/db.py](src/db.py).

The database stores entries in append only files under a base directory and keeps an in memory index for fast lookups. The service provides basic operations: Put, Read, BatchPut, Delete, and ReadKeyRange.

From the project root run:

```bash
uv sync
uv run ./src/main.py
```

The gRPC server listens on port `50051` by default.

## Minimal Python client example


```python
import grpc
import db_api_pb2 as pb
import db_api_pb2_grpc as pb_grpc

def main():
		channel = grpc.insecure_channel('localhost:50051')
		stub = pb_grpc.KeyValueDbStub(channel)

		# Put
		put_req = pb.KeyValue(key='hello', value='world')
		resp = stub.Put(put_req)
		print('Put:', resp.status)

		# Read
		read_req = pb.Key(key='hello')
		resp = stub.Read(read_req)
		print('Read:', resp.status, resp.value)

if __name__ == '__main__':
		main()
```