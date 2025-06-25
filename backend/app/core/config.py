import csv
import json
import pathlib
from pathlib import Path
from typing import List, Dict, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    onestop_api_key: str = ""
    onestop_user_id: str = ""
    supported_jobs: Optional[List[Dict[str, str]]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load supported jobs from the new csv file
        self.supported_jobs = []
        config_path = pathlib.Path(__file__).parent.parent.parent / "config" / "onet_soc_codes.csv"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 1:
                        # Handle the format where title and soc_code are in one quoted string
                        data = row[0]
                        if ',' in data:
                            title, soc_code = data.rsplit(',', 1)
                            self.supported_jobs.append({"title": title.strip(), "soc_code": soc_code.strip()})
        except FileNotFoundError:
            # Handle case where file might not exist
            print(f"Warning: {config_path} not found. Supported jobs list will be empty.")
        except Exception as e:
            print(f"Error loading {config_path}: {e}")

    class Config:
        env_file = ".env"
        field_aliases = {
            "onestop_api_key": "ONESTOP_API_KEY",
            "onestop_user_id": "ONESTOP_USER_ID"
        }


settings = Settings()


def get_settings() -> Settings:
    return settings