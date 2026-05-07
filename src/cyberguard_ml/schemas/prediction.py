"""Pydantic schemas for online inference."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NetworkFlow(BaseModel):
    """One CICIoT2023 flow submitted for scoring."""

    header_length: float = Field(54.0, ge=0)
    protocol_type: int = Field(6, ge=0)
    time_to_live: float = Field(64.0, ge=0, le=255)
    rate: float = Field(120.0, ge=0)
    fin_flag_number: float = Field(0.0, ge=0, le=1)
    syn_flag_number: float = Field(1.0, ge=0, le=1)
    rst_flag_number: float = Field(0.0, ge=0, le=1)
    psh_flag_number: float = Field(0.0, ge=0, le=1)
    ack_flag_number: float = Field(0.0, ge=0, le=1)
    ack_count: float = Field(0.0, ge=0)
    syn_count: float = Field(0.2, ge=0)
    fin_count: float = Field(0.0, ge=0)
    rst_count: float = Field(0.0, ge=0)
    http: float = Field(0.0, ge=0, le=1)
    https: float = Field(0.0, ge=0, le=1)
    dns: float = Field(0.0, ge=0, le=1)
    tcp: float = Field(1.0, ge=0, le=1)
    udp: float = Field(0.0, ge=0, le=1)
    icmp: float = Field(0.0, ge=0, le=1)
    tot_sum: float = Field(567.0, ge=0)
    min_packet_size: float = Field(54.0, ge=0)
    max_packet_size: float = Field(60.0, ge=0)
    avg_packet_size: float = Field(56.7, ge=0)
    std_packet_size: float = Field(0.3, ge=0)
    tot_size: float = Field(56.7, ge=0)
    iat: float = Field(0.00004, ge=0)
    packet_number: float = Field(9.5, ge=0)
    variance: float = Field(0.01, ge=0)
    source_country: str = Field("Morocco")
    destination_server: str = Field("edge-gateway-01")
    source_ip: str = Field("10.42.0.7")


class PredictionResponse(BaseModel):
    """Model scoring response."""

    is_attack: bool
    attack_probability: float
    risk_level: str
    model_version: str
