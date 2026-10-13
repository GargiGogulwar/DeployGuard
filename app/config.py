"""Runtime configuration, read from environment variables.

Only a fixed allow-list of non-sensitive values is ever exposed through the
API/UI. The API token is read here but is never returned or logged.
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str
    version: str
    environment: str
    git_sha: str
    image_tag: str
    build_time: str
    ci_test_status: str
    db_path: str
    api_token: str  # secret: never expose


def get_settings() -> Settings:
    env = os.environ.get
    return Settings(
        app_name="DeployGuard",
        version=env("APP_VERSION", "1.0.0"),
        environment=env("DEPLOYGUARD_ENV", "local"),
        git_sha=env("GIT_SHA", "unknown"),
        image_tag=env("IMAGE_TAG", "local"),
        build_time=env("BUILD_TIME", "unknown"),
        # "passed" is only injected by the CI pipeline after the test job succeeds.
        ci_test_status=env("CI_TEST_STATUS", "not-reported"),
        db_path=env("DEPLOYGUARD_DB_PATH", "data/deployguard.db"),
        api_token=env("DEPLOYGUARD_API_TOKEN", ""),
    )
