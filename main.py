import grpc
import logging
from concurrent import futures
import db_api_pb2_grpc
import db_api_pb2
from context_manager import populate_exception_context

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

class KeyValueDbServicerImpl(db_api_pb2_grpc.KeyValueDbServicer):
    """Implementation of the KeyValueDb service."""

    def Put(self, request: db_api_pb2.KeyValue, context: grpc.ServicerContext) -> db_api_pb2.Response:
        """
        Put a key/value pair
        args:
            request: KeyValue object containing strings key/value to store.
            context: grpc context for handling the request.
        returns:
            Response object containing request status
        """
        try:
            logger.info(f"received Put request: key={request.key}, value={request.value}")
            raise NotImplementedError("Put method not implemented")
        except Exception as e:
            populate_exception_context(context, e)
            return db_api_pb2.Response()
    
    def Read(self, request: db_api_pb2.Key, context: grpc.ServicerContext) -> db_api_pb2.Response:
        """
        Read a value by key
        args:
            request: Key object containing the string key to read.
            context: grpc context for handling the request.
        returns:
            Response object containing request status and the value if the key exists.
        """
        try:
            logger.info(f"received Read request: key={request.key}")
            raise NotImplementedError("Read method not implemented")
        except Exception as e:
            populate_exception_context(context, e)
            return db_api_pb2.Response()

    def ReadKeyRange(self, request: db_api_pb2.KeyRange, context: grpc.ServicerContext) -> db_api_pb2.ResponseList:
        """Read values in a key range
        args:
            request: KeyRange object containing the string start_key and end_key to read.
            context: grpc context for handling the request.
        returns:
            list of Response object containing request status and values in the specified range."""
        try:
            logger.info(f"received ReadKeyRange request: start_key={request.start_key}, end_key={request.end_key}")
            raise NotImplementedError("ReadKeyRange method not implemented")
        except Exception as e:
            populate_exception_context(context, e)
            return db_api_pb2.Response()
        
    def BatchPut(self, request, context):
        """Put multiple key-value pairs.
        args:
            request: BatchPutRequest object containing a list of KeyValue objects to store.
            context: grpc context for handling the request.
        returns:
            list of Response object containing request status."""
        try:
            logger.info(f"received BatchPut request with {len(request.kv_list)} key-value pairs")
            raise NotImplementedError("BatchPut method not implemented")
        except Exception as e:
            populate_exception_context(context, e)
            return db_api_pb2.Response()
        
    def Delete(self, request, context):
        """Delete a key.
        args:
            request: Key object containing the string key to delete.
            context: grpc context for handling the request.
        returns:
            Response object containing request status."""
        try:
            logger.info(f"received Delete request: key={request.key}")
            raise NotImplementedError("Delete method not implemented")
        except Exception as e:
            populate_exception_context(context, e)
            return db_api_pb2.Response()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    db_api_pb2_grpc.add_KeyValueDbServicer_to_server(
        KeyValueDbServicerImpl(), server
    )
    server.add_insecure_port("[::]:50051")
    logger.info("gRPC server started on port 50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
