import logging
from os import path as osp
from textwrap import dedent
import boto3


import pytest
from infrahouse_core.logging import setup_logging
from pytest_infrahouse import terraform_apply

TERRAFORM_ROOT_DIR = "test_data"


LOG = logging.getLogger(__name__)


setup_logging(LOG, debug=True)


@pytest.fixture()
def probe_role(boto3_session, keep_after, test_role_arn, aws_region):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "probe_role")
    # Create service network
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                role_arn     = "{test_role_arn}"
                region       = "{aws_region}"
                trusted_arns = [
                    "arn:aws:iam::990466748045:user/aleks",
                    "{test_role_arn}"
                ]
                """
            )
        )
    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        yield tf_output


def get_boto_client_by_role(service, role_name, test_role_arn, region):
    response = boto3.client("sts").assume_role(
        RoleArn=role_name, RoleSessionName=test_role_arn.split("/")[1]
    )
    # noinspection PyUnresolvedReferences
    return boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    ).client(service, region_name=region)


# Copied from https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/python-example-code.html
"""
This example sets up the KMS Keyring

The AWS KMS keyring uses symmetric encryption KMS keys to generate, encrypt and
decrypt data keys. This example creates a KMS Keyring and then encrypts a custom input EXAMPLE_DATA
with an encryption context. This example also includes some sanity checks for demonstration:
1. Ciphertext and plaintext data are not the same
2. Encryption context is correct in the decrypted message header
3. Decrypted plaintext value matches EXAMPLE_DATA
These sanity checks are for demonstration in the example only. You do not need these in your code.

AWS KMS keyrings can be used independently or in a multi-keyring with other keyrings
of the same or a different type.

"""
from aws_cryptographic_material_providers.mpl import AwsCryptographicMaterialProviders
from aws_cryptographic_material_providers.mpl.config import MaterialProvidersConfig
from aws_cryptographic_material_providers.mpl.models import CreateAwsKmsKeyringInput
from aws_cryptographic_material_providers.mpl.references import IKeyring
from typing import Dict  # noqa pylint: disable=wrong-import-order

import aws_encryption_sdk
from aws_encryption_sdk import CommitmentPolicy


def encrypt_with_keyring(
    plain_text: bytes,
    kms_key_arn: str,
    encryption_context: dict = None,
    kms_client=None,
    region: str = None,
) -> bytes:
    """Demonstrate an encrypt function using an AWS KMS keyring.

    Usage: encrypt_with_keyring(kms_key_arn)
    :param plain_text: Plain text message
    :param kms_key_arn: KMS Key ARN for the KMS key you want to use for encryption.
    :type kms_key_arn: string
    :param encryption_context: Something non-secret that describes the plain text message content.
    :type encryption_context: dict
    :param kms_client: Pass a specific KMS boto client. Otherwise, the function will create its own.
    :param region: If the function creates a KMS client, use this region.
    :return: Encrypted message
    :rtype: bytes
    """
    print(f"{kms_key_arn = }")
    encryption_context = encryption_context or {}
    # 1. Instantiate the encryption SDK client.
    # This builds the client with the REQUIRE_ENCRYPT_REQUIRE_DECRYPT commitment policy,
    # which enforces that this client only encrypts using committing algorithm suites and enforces
    # that this client will only decrypt encrypted messages that were created with a committing
    # algorithm suite.
    # This is the default commitment policy if you were to build the client as
    # `client = aws_encryption_sdk.EncryptionSDKClient()`.
    client = aws_encryption_sdk.EncryptionSDKClient(
        commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT
    )

    # 2. Create a boto3 client for KMS.
    kms_client = kms_client or boto3.client("kms", region_name=region)

    # 3. Optional: create encryption context.
    # Remember that your encryption context is NOT SECRET.
    # encryption_context: Dict[str, str] = {
    #     "encryption": "context",
    #     "is not": "secret",
    #     "but adds": "useful metadata",
    #     "that can help you": "be confident that",
    #     "the data you are handling": "is what you think it is",
    # }

    # 4. Create your keyring
    mat_prov: AwsCryptographicMaterialProviders = AwsCryptographicMaterialProviders(
        config=MaterialProvidersConfig()
    )

    keyring_input: CreateAwsKmsKeyringInput = CreateAwsKmsKeyringInput(
        kms_key_id=kms_key_arn, kms_client=kms_client
    )

    kms_keyring: IKeyring = mat_prov.create_aws_kms_keyring(input=keyring_input)

    # 5. Encrypt the data with the encryptionContext.
    ciphertext, _ = client.encrypt(
        source=plain_text, keyring=kms_keyring, encryption_context=encryption_context
    )

    # 6. Demonstrate that the ciphertext and plaintext are different.
    # (This is an example for demonstration; you do not need to do this in your own code.)
    assert (
        ciphertext != plain_text
    ), "Ciphertext and plaintext data are the same. Invalid encryption"

    # 7. Decrypt your encrypted data using the same keyring you used on encrypt.
    plaintext_bytes, _ = client.decrypt(
        source=ciphertext,
        keyring=kms_keyring,
        # Provide the encryption context that was supplied to the encrypt method
        encryption_context=encryption_context,
    )

    # 8. Demonstrate that the decrypted plaintext is identical to the original plaintext.
    # (This is an example for demonstration; you do not need to do this in your own code.)
    assert (
        plaintext_bytes == plaintext_bytes
    ), "Decrypted plaintext should be identical to the original plaintext. Invalid decryption"

    return ciphertext


def decrypt_with_keyring(
    ciphertext: bytes,
    kms_key_arn: str,  # e.g. arn:aws:kms:us-west-1:611021602836:key/f6ad1722-9809-468e-b729-a3cb74f0b8dc
    encryption_context: dict = None,
    kms_client=None,
    region: str = None,
) -> bytes:
    """Demonstrate how to decrypt cycle using an AWS KMS keyring.

    Usage: decrypt_with_keyring(ciphertext, kms_key_arn)

    :param ciphertext: bytes
    :param kms_key_arn: KMS Key identifier for the KMS key you want to use for decryption of your data keys.
    :type kms_key_arn: string
    :param encryption_context: Something non-secret that describes the plain text message content.
    :type encryption_context: dict
    :param kms_client: Pass a specific KMS boto client. Otherwise, the function will create its own.
    :param region: If the function creates a KMS client, use this region.
    :return: Plain text message
    :rtype: str
    """
    encryption_context = encryption_context or {}
    # 1. Instantiate the encryption SDK client.
    # This builds the client with the REQUIRE_ENCRYPT_REQUIRE_DECRYPT commitment policy,
    # which enforces that this client only encrypts using committing algorithm suites and enforces
    # that this client will only decrypt encrypted messages that were created with a committing
    # algorithm suite.
    # This is the default commitment policy if you were to build the client as
    # `client = aws_encryption_sdk.EncryptionSDKClient()`.
    client = aws_encryption_sdk.EncryptionSDKClient(
        commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT
    )

    # 2. Create a boto3 client for KMS.
    kms_client = kms_client or boto3.client("kms", region_name=region)

    # 3. Optional: create encryption context.
    # Remember that your encryption context is NOT SECRET.
    # encryption_context: Dict[str, str] = {
    #     "encryption": "context",
    #     "is not": "secret",
    #     "but adds": "useful metadata",
    #     "that can help you": "be confident that",
    #     "the data you are handling": "is what you think it is",
    # }

    # 4. Create your keyring
    mat_prov: AwsCryptographicMaterialProviders = AwsCryptographicMaterialProviders(
        config=MaterialProvidersConfig()
    )

    keyring_input: CreateAwsKmsKeyringInput = CreateAwsKmsKeyringInput(
        kms_key_id=kms_key_arn, kms_client=kms_client
    )

    kms_keyring: IKeyring = mat_prov.create_aws_kms_keyring(input=keyring_input)

    # 5. Decrypt your encrypted data using the same keyring you used on encrypt.
    plaintext_bytes, _ = client.decrypt(
        source=ciphertext,
        keyring=kms_keyring,
        # Provide the encryption context that was supplied to the encrypt method
        encryption_context=encryption_context,
    )

    return plaintext_bytes
