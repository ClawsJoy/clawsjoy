"""安全网关 - 敏感信息过滤"""

import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class SecurityGate:
    """安全网关 - 介于用户和LLM之间"""

    PATTERNS = {
        "api_key": [
            r'api_key["\s:]+["\']?([a-zA-Z0-9_\-]{10,})["\']?',
            r'API_KEY\s*=\s*["\']([a-zA-Z0-9_\-]+)["\']',
            r'"api_key"\s*:\s*"([^"]+)"',
        ],
        "password": [
            r'password["\s:]+["\']?([^"\'\s]{6,})["\']?',
            r'密码[是为]?\s*["\']?([^"\'\s，,]{4,})["\']?',
            r'pwd\s*=\s*["\']([^"\']+)["\']',
        ],
        "email": [
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        ],
        "token": [
            r'token["\s:]+["\']?(ya29\.[a-zA-Z0-9_\-\.]+)["\']?',
            r'Bearer\s+([a-zA-Z0-9_\-\.]+)',
        ],
    }

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.vault_path = Path(f"data/security_vault/{tenant_id}")
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self._vault = self._load_vault()

    def _load_vault(self) -> Dict:
        vault_file = self.vault_path / "secrets.json"
        if vault_file.exists():
            with open(vault_file, 'r') as f:
                return json.load(f)
        return {"secrets": {}}

    def _save_vault(self):
        vault_file = self.vault_path / "secrets.json"
        with open(vault_file, 'w') as f:
            json.dump(self._vault, f, indent=2)

    def _generate_placeholder(self, secret_type: str, value: str) -> str:
        short_hash = hashlib.md5(value.encode()).hexdigest()[:8]
        return f"[{secret_type.upper()}_{short_hash}]"

    def process_input(self, text: str, user_id: str = "anonymous") -> Tuple[str, List[Dict]]:
        sanitized = text
        extracted = []

        for stype, patterns in self.PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, sanitized, re.IGNORECASE)
                for match in matches:
                    value = match if isinstance(match, str) else match[-1]
                    if len(str(value)) < 4:
                        continue

                    placeholder = self._generate_placeholder(stype, value)
                    secret_id = hashlib.md5(f"{self.tenant_id}{user_id}{value}".encode()).hexdigest()[:16]

                    self._vault['secrets'][secret_id] = {
                        'id': secret_id, 'user_id': user_id, 'type': stype,
                        'value': value, 'placeholder': placeholder,
                        'created_at': datetime.now().isoformat()
                    }
                    extracted.append({'type': stype, 'placeholder': placeholder})
                    sanitized = sanitized.replace(str(value), placeholder)

        if extracted:
            self._save_vault()
        return sanitized, extracted

    def process_output(self, text: str, user_id: str = "anonymous") -> str:
        restored = text
        for secret_id, record in self._vault['secrets'].items():
            if record.get('user_id') != user_id:
                continue
            if record['placeholder'] in restored:
                value = record['value']
                masked = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
                restored = restored.replace(record['placeholder'], f"[{record['type']}:{masked}]")
        return restored

    def get_stats(self) -> Dict:
        return {
            'tenant_id': self.tenant_id,
            'total_secrets': len(self._vault['secrets']),
            'vault_path': str(self.vault_path)
        }

security_gate = SecurityGate()
