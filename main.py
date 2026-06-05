from webbrowser import get

import grpc
from logger import get_logger
from concurrent import futures
import db_api_pb2_grpc
import db_api_pb2
from context_manager import populate_exception_context
from config_manager import get_config
from dotenv import load_dotenv
from db import DB

load_dotenv()  # Load environment variables from .env file

logger = get_logger(__name__)

class KeyValueDbServicerImpl(db_api_pb2_grpc.KeyValueDbServicer):
    """Implementation of the KeyValueDb service."""

    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.db = DB()


    def Put(self, request: db_api_pb2.KeyValue, context: grpc.ServicerContext) -> db_api_pb2.Response: # type: ignore
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
            self.db.write(request.key, request.value)
            return db_api_pb2.Response(status=db_api_pb2.google_dot_rpc_dot_status__pb2.Status(code=grpc.StatusCode.OK.value[0], message="Success")) # type: ignore
        except Exception as e:
            logger.error(f"Error in Put method: {e}")
            populate_exception_context(context, e)
            return db_api_pb2.Response() # type: ignore
    
    def Read(self, request: db_api_pb2.Key, context: grpc.ServicerContext) -> db_api_pb2.Response: # type: ignore
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
            logger.error(f"Error in Read method: {e}")
            populate_exception_context(context, e)
            return db_api_pb2.Response() # type: ignore

    def ReadKeyRange(self, request: db_api_pb2.KeyRange, context: grpc.ServicerContext) -> db_api_pb2.ResponseList: # type: ignore
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
            logger.error(f"Error in ReadKeyRange method: {e}")
            populate_exception_context(context, e)
            return db_api_pb2.Response() # type: ignore
        
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
            logger.error(f"Error in BatchPut method: {e}")
            populate_exception_context(context, e)
            return db_api_pb2.Response() # type: ignore
        
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
            logger.error(f"Error in Delete method: {e}")
            populate_exception_context(context, e)
            return db_api_pb2.Response() # type: ignore

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
