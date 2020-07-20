from typing import Optional, Any, Dict, Set

def _resolve_common_key(primary: Optional[Any], secondary: Optional[Any]) -> Optional[Any]:
    if primary is not None and secondary is not None and isinstance(primary, dict) and isinstance(secondary, dict):
        return merge_dicts(primary, secondary)

    # If key is present in primary and secondary, always use primary value
    return primary

def merge_dicts(primary_content: Dict, secondary_content: Dict) -> Dict:
    primary_keys: Set[str] = set(primary_content.keys())
    secondary_keys: Set[str] = set(secondary_content.keys())

    ret: Dict = {}

    for key in primary_keys - secondary_keys:
        ret[key] = primary_content[key]
    for key in secondary_keys - primary_keys:
        ret[key] = secondary_content[key]

    for key in primary_keys.intersection(secondary_keys):
        ret[key] = _resolve_common_key(primary_content[key], secondary_content[key])

    return ret