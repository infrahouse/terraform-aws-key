import json
from os import path as osp
from textwrap import dedent

from pytest_infrahouse import terraform_apply

from tests.conftest import (
    LOG,
    TERRAFORM_ROOT_DIR,
    encrypt_with_keyring,
    decrypt_with_keyring,
    get_boto_client_by_role,
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

        kms_client = get_boto_client_by_role(
            "kms", probe_role_arn, test_role_arn, aws_region
        )
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
