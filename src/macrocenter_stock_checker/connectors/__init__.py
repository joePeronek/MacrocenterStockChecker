"""Connector interfaces and implementations."""

from .base import BaseConnector, ParsedSnapshot
from .macrocenter import MacrocenterConnector

__all__ = ["BaseConnector", "MacrocenterConnector", "ParsedSnapshot"]
