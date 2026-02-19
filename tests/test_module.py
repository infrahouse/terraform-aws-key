import json
from os import path as osp
from textwrap import dedent

import pytest
from botocore.exceptions import ClientError
from infrahouse_core.aws import get_client
from pytest_infrahouse import terraform_apply

from tests.conftest import (
    LOG,
    TERRAFORM_ROOT_DIR,
    encrypt_with_keyring,
    decrypt_with_keyring,
)


def test_module(
    probe_role,
    test_role_arn,
    keep_after,
    aws_region,
    boto3_session,
):
    probe_role_arn = probe_role["role_arn"]["value"]

    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "key")
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

        kms_client = get_client("kms", role_arn=probe_role_arn, region=aws_region)
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

        kms_client = get_client("kms", role_arn=probe_role_arn, region=aws_region)

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

        kms_client = get_client("kms", role_arn=probe_role_arn, region=aws_region)

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
