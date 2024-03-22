class NexarClientError(Exception):
  pass


class NexarClientUnauthenticatedError(NexarClientError):
  pass

class NexarClientBadRequestError(NexarClientError):
  pass

class NexarClientRequestFailedError(NexarClientError):
  pass

class NexarClientUploadError(NexarClientError):
  def __init__(self):
    super().__init__("Error while uploading file to Nexar")
