from pydantic import BaseModel

class URLRequest(BaseModel):
    url1: str
    url2: str

class TopicRequest(BaseModel):
    topic: str