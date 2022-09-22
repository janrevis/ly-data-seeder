from uuid import uuid4

farmers_market_mapping = {
    "mappings": {
        "properties": {
            "usda_id": {"type": "text"},
            "name": {"type": "text"},
            "location_x": {"type": "float"},
            "location_y": {"type": "float"},
            "address": {"type": "text"},
            "data": { "type": "object" }
        }
    }
}

def create_mapping(entry):
  mapping = {
    "mappings": {
      "properties": {
        "id": uuid4(),
        "name": entry["name"],
        "address": entry["address"],
        "location": {
          "x": float(entry["x"]),
          "y": float(entry("y")),    
        }
      }
    } 
  }
  if entry["usda_id"] != None:
    mapping["usda_id"] = entry["usda_id"]
  return mapping
