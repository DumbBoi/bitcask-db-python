import grpc

def populate_exception_context(context: grpc.ServicerContext, exception: Exception) -> None:
    """Function to populate the context with exception status and message."""
    if exception is None:
        context.set_code(grpc.StatusCode.OK)
        context.set_details("Success")
        return
    if isinstance(exception, KeyError):
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(str(exception))
        return
    if isinstance(exception, NotImplementedError):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details(str(exception))
        return
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_details(str(exception) if exception else "Unindentified internal error")