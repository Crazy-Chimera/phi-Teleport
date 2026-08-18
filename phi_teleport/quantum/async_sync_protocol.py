"""
Asynchronous classical synchronization protocol for teleportation nodes.
"""

import time
import logging
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class SyncMessage:
    """A single synchronization message."""
    sender_id: str
    receiver_id: str
    timestamp: float
    sequence: int
    payload: dict


class AsyncSyncProtocol:
    """Classical synchronization channel between two nodes.

    Parameters
    -
    retries : int
        Number of retries for failed sends.
    retry_delay : float
        Delay between retries, in seconds.
    """

    def __init__(self, retries: int = 3, retry_delay: float = 0.1):
        self.retries = retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
        self.sent = []
        self.received = []
        self.last_sequence = 0

    def send(self, sender_id: str, receiver_id: str,
             payload: dict) -> SyncMessage:
        """Send a synchronization message with retry logic."""
        for attempt in range(self.retries + 1):
            try:
                self.last_sequence += 1
                msg = SyncMessage(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    timestamp=time.time(),
                    sequence=self.last_sequence,
                    payload=payload,
                )
                self.sent.append(msg)
                return msg
            except Exception:
                if attempt < self.retries:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def receive(self, msg: SyncMessage) -> None:
        """Receive a message and store it in the log."""
        self.received.append(msg)

    def synchronize(self, sender_id: str, receiver_id: str) -> float:
        """Perform a complete synchronization handshake.

        Returns the median one‑way latency in seconds.
        """
        start = time.time()
        handshake = self.send(sender_id, receiver_id, {'type': 'handshake'})
        # Simulated echo from the receiver.
        self.receive(SyncMessage(
            sender_id=receiver_id,
            receiver_id=sender_id,
            timestamp=time.time(),
            sequence=handshake.sequence,
            payload={'type': 'handshake_ack'},
        ))
        end = time.time()
        return (end - start) / 2.0
