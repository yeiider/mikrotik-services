from pydantic import BaseModel

class RouterConfig(BaseModel):
    host: str
    port: int = 8728
    username: str
    password: str
    alias: str
    use_ssl: bool = False
    ssl_verify: bool = False
