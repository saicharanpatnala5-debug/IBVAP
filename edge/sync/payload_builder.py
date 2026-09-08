"""
IBVAP - Compressed Batch Payload Packaging & Digest Generation
Compresses offline event batches for satellite & low-bandwidth backhaul.
"""

import zlib
import json
import hashlib
from typing import List, Dict, Any, Tuple

class PayloadBuilder:
    def pack_events(self, node_id: str, events: List[Dict[str, Any]]) -> Tuple[bytes, str, Dict[str, Any]]:
        """
        Packs, computes SHA-256 digest, and compresses event batch.
        Returns: (compressed_bytes, sha256_digest, metadata)
        """
        raw_dict = {
            "edge_node_id": node_id,
            "event_count": len(events),
            "events": events
        }
        raw_json = json.dumps(raw_dict).encode("utf-8")
        digest = hashlib.sha256(raw_json).hexdigest()
        compressed = zlib.compress(raw_json, level=6)

        meta = {
            "uncompressed_bytes": len(raw_json),
            "compressed_bytes": len(compressed),
            "compression_ratio": round(len(raw_json) / max(len(compressed), 1), 2),
            "sha256": digest
        }
        return compressed, digest, meta

payload_builder = PayloadBuilder()
