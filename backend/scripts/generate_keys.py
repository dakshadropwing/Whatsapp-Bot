"""
Script to generate JWT keys, Flask App secret, and DB encryption keys.
Writes them to .env in both root and backend folders.
"""
from __future__ import annotations

import os
import secrets
import sys

# Try to import cryptography, install if missing
try:
    from cryptography.fernet import Fernet
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
    from cryptography.fernet import Fernet


def generate_secrets() -> dict[str, str]:
    # Flask secret: 32 hex chars
    app_secret = secrets.token_hex(32)
    # JWT secret: 32 hex chars
    jwt_secret = secrets.token_hex(32)
    # Master key: Fernet key (since the app might use Fernet or AES)
    master_key = Fernet.generate_key().decode()
    
    return {
        "APP_SECRET_KEY": app_secret,
        "JWT_SECRET_KEY": jwt_secret,
        "ENCRYPTION_MASTER_KEY": master_key,
    }


def update_env_file(env_path: str, example_path: str, secrets_dict: dict[str, str]) -> None:
    if not os.path.exists(example_path):
        print(f"Example env file not found at {example_path}")
        return

    # If .env doesn't exist, start by copying .env.example
    if not os.path.exists(env_path):
        with open(example_path, "r") as f:
            content = f.read()
        print(f"Creating new .env at {env_path} from template...")
    else:
        with open(env_path, "r") as f:
            content = f.read()
        print(f"Updating existing .env at {env_path}...")

    # Replace values
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            if key in secrets_dict:
                # Replace with the generated value
                lines[i] = f"{key}={secrets_dict[key]}"

    # Write out the updated .env
    with open(env_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Successfully wrote {env_path}")


def main() -> None:
    print("🔑 Generating secure platform keys...")
    secrets_dict = generate_secrets()

    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    root_dir = os.path.dirname(backend_dir)

    root_example = os.path.join(root_dir, ".env.example")
    root_env = os.path.join(root_dir, ".env")
    backend_env = os.path.join(backend_dir, ".env")

    # Write env files
    update_env_file(root_env, root_example, secrets_dict)
    update_env_file(backend_env, root_example, secrets_dict)
    
    print("🎉 Keys generated and environment configured successfully!")


if __name__ == "__main__":
    main()
