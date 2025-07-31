import json
from os import path as osp
from textwrap import dedent

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

    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "key")
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                    region              = "{aws_region}"
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

        cipher_text = encrypt_with_keyring(
            plaintext_message,
            kms_key_arn,
            kms_client=boto3_session.client("kms", region_name=aws_region),
        )
        assert (
            decrypt_with_keyring(
                cipher_text,
                kms_key_arn,
                kms_client=boto3_session.client("kms", region_name=aws_region),
            )
            == plaintext_message
        )
