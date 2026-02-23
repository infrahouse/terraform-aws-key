# Troubleshooting

## Common Issues

### AccessDeniedException when encrypting or decrypting

**Symptom:**

```
An error occurred (AccessDeniedException) when calling the Encrypt operation
```

**Causes:**

1. **Role not in the key policy.** Ensure the IAM role ARN is listed in `key_users`,
   `key_encrypt_only_users`, or `key_decrypt_only_users` as appropriate.

2. **Encrypt-only role trying to decrypt.** If the role is in `key_encrypt_only_users`,
   it cannot decrypt. Move it to `key_users` if it needs both.

3. **Decrypt-only role trying to encrypt.** If the role is in `key_decrypt_only_users`,
   it cannot encrypt. Move it to `key_users` if it needs both.

4. **IAM policy denying KMS access.** Even if the key policy allows the role, the role's
   IAM policy must also allow the KMS actions. Check for explicit `Deny` statements.

5. **IAM propagation delay.** After creating or modifying IAM roles, allow a few seconds
   for changes to propagate before attempting KMS operations.

### Key policy is invalid

**Symptom:**

```
MalformedPolicyDocumentException: Policy contains a statement with one or more invalid principals.
```

**Cause:** An ARN in one of the user lists is malformed or refers to a non-existent IAM role.

**Fix:** Verify all ARNs in `key_users`, `key_encrypt_only_users`, and
`key_decrypt_only_users` are valid and the roles exist.

### Key alias already exists

**Symptom:**

```
AlreadyExistsException: An alias with the name arn:aws:kms:...:alias/my-key already exists
```

**Cause:** A KMS alias with the same name already exists in the account/region.

**Fix:** Use a different `key_name` or import the existing alias into your Terraform state.

### Cannot delete key

**Symptom:** `terraform destroy` appears to hang or takes a long time.

**Explanation:** AWS KMS keys have a mandatory waiting period (7-30 days) before deletion.
Terraform schedules the key for deletion and the destroy completes, but the key remains
in `PendingDeletion` state in AWS until the waiting period expires.

## Getting Help

- [Open an issue](https://github.com/infrahouse/terraform-aws-key/issues)
- [Contact InfraHouse](https://infrahouse.com/contact)
