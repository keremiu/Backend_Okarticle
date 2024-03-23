from pydantic import BaseModel
from typing import Optional, List
from fastapi import  UploadFile,File
class PDF(BaseModel):
    file: UploadFile = File(...)
    string: Optional[str]
#sorunlar var

'''UploadFile doğrudan bir Pydantic modelinde kullanılamaz
çünkü UploadFile bir form verisi olarak alınmalıdır ve Pydantic modelleri genellikle JSON verisi için kullanılır.'''
