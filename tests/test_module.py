import json
from os import path as osp
from os import remove
from shutil import rmtree
from textwrap import dedent

import boto3
import pytest
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from pytest_infrahouse import terraform_apply

from tests.conftest import (
    LOG,
    TERRAFORM_ROOT_DIR,
    encrypt_with_keyring,
    decrypt_with_keyring,
)


def get_probe_client(
    boto3_session: boto3.Session, service_name: str, role_arn: str, region: str
) -> BaseClient:
    """Assume a probe role via the test session and return a service client.

    :param boto3_session: A boto3 session with credentials trusted by the probe role.
    :param service_name: AWS service name (e.g., "kms").
    :param role_arn: The ARN of the probe role to assume.
    :param region: AWS region name.
    :return: A boto3 client for the specified service using probe role credentials.
    """
    sts = boto3_session.client("sts", region_name=region)
    response = sts.assume_role(RoleArn=role_arn, RoleSessionName="probe-role-test")
    creds = response["Credentials"]
    probe_session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=region,
    )
    return probe_session.client(service_name, region_name=region)


@pytest.mark.parametrize(
    "aws_provider_version", ["~> 5.62", "~> 6.0"], ids=["aws-5", "aws-6"]
)
def test_module(
    probe_role,
    test_role_arn,
    keep_after,
    aws_region,
    boto3_session,
    aws_provider_version,
):
    """Test that key_users can both encrypt and decrypt."""
    probe_role_arn = probe_role["role_arn"]["value"]

    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "key")

    # Clean up state so Terraform re-inits with the specified provider version
    for state_path in [
        osp.join(terraform_module_dir, ".terraform"),
        osp.join(terraform_module_dir, ".terraform.lock.hcl"),
    ]:
        try:
            if osp.isdir(state_path):
                rmtree(state_path)
            elif osp.isfile(state_path):
                remove(state_path)
        except FileNotFoundError:
            pass

    with open(osp.join(terraform_module_dir, "terraform.tf"), "w") as fp:
        fp.write(
            dedent(
                f"""\
                terraform {{
                  required_version = "~> 1.5"
                  required_providers {{
                    aws = {{
                      source  = "hashicorp/aws"
                      version = "{aws_provider_version}"
                    }}
                    random = {{
                      source  = "hashicorp/random"
                      version = "~> 3.6"
                    }}
                  }}
                }}
                """
            )
        )

    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                    region              = "{aws_region}"
                    key_users = ["{probe_role_arn}"]
                    """
            )
        )
        if test_role_arn:
            fp.write(
                dedent(
                    f"""
                    role_arn        = "{test_role_arn}"
                    """
                )
            )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        kms_key_arn = tf_output["kms_key_arn"]["value"]
        plaintext_message = b"Hello world"

        kms_client = get_probe_client(boto3_session, "kms", probe_role_arn, aws_region)
        cipher_text = encrypt_with_keyring(
            plaintext_message,
            kms_key_arn,
            kms_client=kms_client,
        )
        assert (
            decrypt_with_keyring(
                cipher_text,
                kms_key_arn,
                kms_client=kms_client,
            )
            == plaintext_message
        )


def test_encrypt_only_permissions(
    probe_role,
    test_role_arn,
    keep_after,
    aws_region,
    boto3_session,
):
    """Test that encrypt-only users can encrypt but not decrypt."""
    probe_role_arn = probe_role["role_arn"]["value"]

    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "key")
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                    region                 = "{aws_region}"
                    key_encrypt_only_users = ["{probe_role_arn}"]
                    """
            )
        )
        if test_role_arn:
            fp.write(
                dedent(
                    f"""
                    role_arn        = "{test_role_arn}"
                    """
                )
            )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        kms_key_arn = tf_output["kms_key_arn"]["value"]

        kms_client = get_probe_client(boto3_session, "kms", probe_role_arn, aws_region)

        # Encrypt should succeed
        response = kms_client.encrypt(
            KeyId=kms_key_arn,
            Plaintext=b"Hello world",
        )
        ciphertext_blob = response["CiphertextBlob"]
        assert ciphertext_blob is not None

        # Decrypt should fail with AccessDeniedException
        with pytest.raises(ClientError) as exc_info:
            kms_client.decrypt(
                KeyId=kms_key_arn,
                CiphertextBlob=ciphertext_blob,
            )
        assert exc_info.value.response["Error"]["Code"] == "AccessDeniedException"


def test_decrypt_only_permissions(
    probe_role,
    test_role_arn,
    keep_after,
    aws_region,
    boto3_session,
):
    """Test that decrypt-only users can decrypt but not encrypt."""
    probe_role_arn = probe_role["role_arn"]["value"]

    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "key")
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                    region                 = "{aws_region}"
                    key_decrypt_only_users = ["{probe_role_arn}"]
                    """
            )
        )
        if test_role_arn:
            fp.write(
                dedent(
                    f"""
                    role_arn        = "{test_role_arn}"
                    """
                )
            )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        kms_key_arn = tf_output["kms_key_arn"]["value"]

        # Use admin session to produce ciphertext (root account has kms:*)
        admin_kms_client = boto3_session.client("kms", region_name=aws_region)
        response = admin_kms_client.encrypt(
            KeyId=kms_key_arn,
            Plaintext=b"Hello world",
        )
        ciphertext_blob = response["CiphertextBlob"]

        kms_client = get_probe_client(boto3_session, "kms", probe_role_arn, aws_region)

        # Decrypt should succeed
        response = kms_client.decrypt(
            KeyId=kms_key_arn,
            CiphertextBlob=ciphertext_blob,
        )
        assert response["Plaintext"] == b"Hello world"

        # Encrypt should fail with AccessDeniedException
        with pytest.raises(ClientError) as exc_info:
            kms_client.encrypt(
                KeyId=kms_key_arn,
                Plaintext=b"Hello world",
            )
        assert exc_info.value.response["Error"]["Code"] == "AccessDeniedException"
