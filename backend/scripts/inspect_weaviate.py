import weaviate
import json
from config import get_settings

def inspect():
    settings = get_settings()
    client = weaviate.connect_to_local(
        host=settings.weaviate_url.split("//")[-1].split(":")[0],
        port=int(settings.weaviate_url.split(":")[-1])
    )

    collection = client.collections.get(settings.weaviate_collection_name)
    response = collection.query.fetch_objects(limit=1)

    for obj in response.objects:
        print(f"ID: {obj.uuid}")
        print(f"Properties: {json.dumps(obj.properties, indent=2)}")
        if obj.vector:
            print(f"Vector present: Yes")

    client.close()

if __name__ == "__main__":
    try:
        inspect()
    except Exception as e:
        print(f"Error: {e}")
