import json
from pathlib import Path

from app.main import app


def generate_openapi():
    openapi_schema = app.openapi()

    # Resolve the path to save the schema at the root of apps/backend
    current_dir = Path(__file__).resolve().parent
    backend_dir = current_dir.parent.parent
    output_path = backend_dir / "openapi.json"

    with output_path.open("w") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"Generated OpenAPI schema successfully at {output_path}")


if __name__ == "__main__":
    generate_openapi()
