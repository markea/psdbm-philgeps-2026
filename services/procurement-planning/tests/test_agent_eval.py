import json
import os
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def load_golden_dataset():
    dataset_path = os.path.join(os.path.dirname(__file__), 'golden_dataset.json')
    with open(dataset_path, 'r') as f:
        return json.load(f)

dataset = load_golden_dataset()

@pytest.mark.parametrize("scenario", dataset)
def test_agent_golden_dataset(scenario):
    query = scenario.get("query")
    agent_id = scenario.get("agent_id")
    golden_keywords = scenario.get("golden_keywords", [])
    
    response = client.post(
        "/api/v1/agent/chat",
        json={"agent_id": agent_id, "message": query}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    reply = data.get("reply", "")
    
    # Assert that all golden keywords are present in the response
    missing_keywords = []
    for keyword in golden_keywords:
        if keyword.lower() not in reply.lower():
            missing_keywords.append(keyword)
            
    assert not missing_keywords, f"Agent '{agent_id}' hallucination or incomplete answer! Missing keywords for query '{query}': {missing_keywords}. Original reply: {reply}"
