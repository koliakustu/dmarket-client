import json
import os
import dotenv
from dmarket.client import DMarketClient

def main():
    dotenv.load_dotenv()
    public_key = os.getenv("DMARKET_PUBLIC_KEY")
    secret_key = os.getenv("DMARKET_SECRET_KEY")
    client = DMarketClient(public_key, secret_key)

if __name__ == "__main__":
    main()
