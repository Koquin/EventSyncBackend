from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional


class RegistrationStatus(str, Enum):
    AGUARDANDO_PAGAMENTO = "aguardando_pagamento"
    APROVADA = "aprovada"
    RECUSADA = "recusada"
    CANCELADA = "cancelada"
    FINALIZADA = "finalizada"


class RegistrationCreate(BaseModel):
    event_id: str = Field(alias="eventoId")
    status: RegistrationStatus = RegistrationStatus.AGUARDANDO_PAGAMENTO
    
    class Config:
        populate_by_name = True


class Registration(BaseModel):
    id: str
    evento_id: str = Field(alias="eventoId")
    usuario_id: str = Field(alias="usuarioId")
    status: RegistrationStatus
    timestamp_inscricao: datetime = Field(alias="timestampInscricao")
    timestamp_pagamento: Optional[datetime] = Field(None, alias="timestampPagamento")
    
    class Config:
        populate_by_name = True


class RegistrationResponse(BaseModel):
    id: str
    event_id: str = Field(alias="eventId")
    event_name: str = Field(alias="eventName")
    event_date: str = Field(alias="eventDate")
    event_banner: str = Field(alias="eventBanner")
    status: RegistrationStatus
    timestamp_inscricao: datetime = Field(alias="timestampInscricao")
    timestamp_pagamento: Optional[datetime] = Field(None, alias="timestampPagamento")
    can_cancel: bool = Field(alias="canCancel")
    
    class Config:
        populate_by_name = True


class RegistrationWithUser(BaseModel):
    id: str
    evento_id: str = Field(alias="eventoId")
    usuario_id: str = Field(alias="usuarioId")
    user_name: str = Field(alias="userName")
    user_email: str = Field(alias="userEmail")
    user_city: str = Field(alias="userCity")
    status: RegistrationStatus
    timestamp_inscricao: datetime = Field(alias="timestampInscricao")
    timestamp_pagamento: Optional[datetime] = Field(None, alias="timestampPagamento")
    
    class Config:
        populate_by_name = True


class RegistrationInDB(BaseModel):
    id: str
    evento_id: str
    usuario_id: str
    status: RegistrationStatus
    timestamp_inscricao: datetime
    timestamp_pagamento: Optional[datetime] = None
