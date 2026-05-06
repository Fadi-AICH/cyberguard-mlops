"""Pydantic schemas for online inference."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NetworkFlow(BaseModel):
    """One network flow submitted for scoring."""

    protocol_type: str = Field("tcp", examples=["tcp", "udp", "icmp"])
    service: str = Field("https", examples=["http", "https", "dns", "ssh", "unknown"])
    flag: str = Field("SF", examples=["SF", "S0", "REJ", "RSTO"])
    duration: float = Field(0.42, ge=0)
    src_bytes: float = Field(920.0, ge=0)
    dst_bytes: float = Field(210.0, ge=0)
    count: int = Field(18, ge=0)
    srv_count: int = Field(11, ge=0)
    serror_rate: float = Field(0.05, ge=0, le=1)
    same_srv_rate: float = Field(0.88, ge=0, le=1)
    dst_host_srv_count: int = Field(57, ge=0)
    dst_host_same_srv_rate: float = Field(0.92, ge=0, le=1)
    logged_in: int = Field(1, ge=0, le=1)
    urgent: int = Field(0, ge=0)
    failed_logins: int = Field(0, ge=0)
    payload_entropy: float = Field(4.1, ge=0, le=8)
    packet_rate: float = Field(23.0, ge=0)


class PredictionResponse(BaseModel):
    """Model scoring response."""

    is_attack: bool
    attack_probability: float
    risk_level: str
    model_version: str
