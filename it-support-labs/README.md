# IT support casebook

These reproducible demonstrations accompany Rehman Nadeem’s work in infrastructure and AI-assisted support at Armans.AI. The exercises use fictional records. The customer updates below illustrate how a technician can turn a check into a useful handover.

| Work sample | What the evidence shows | Next human decision |
|---|---|---|
| Microsoft Entra ID sign-in triage | An editor receives 50076 and later signs in to the same app. A contractor receives 53003. An unrecognized error is queued for review. | The later success shows that the editor got in. The contractor's record does not identify which policy blocked access. An authorized administrator must inspect the matching sign-in in the tenant. |
| Cisco-style trunk investigation | VLAN 20 is absent on the distribution side in a pair of synthetic trunk snapshots. After the fixture change, it passes both sides. VLAN 10 passes throughout and VLAN 99 remains excluded. | The sample verifies the supplied state. A technician would also test endpoint connectivity before closing a real ticket. |
| Service desk data analysis with SQL | Of twelve tickets, eight are closed and four remain open. Two of the eight closed tickets missed their time target. Cases completed exactly at target count as on time. | Investigate the two late tickets and review open cases separately. No creation timestamps are supplied to assess how long the open cases have been waiting. |
| Windows PowerShell recovery | The script archives a fictional shift handover, deliberately changes the working copy, verifies the archived candidate against the original hash, and verifies the restored file again. | Use the runner log to compare the damaged, original and restored hashes. All file writes are confined to a newly created temporary directory. |
| AWS S3 version recovery | An in-process Moto emulator receives two object versions. The script copies the known-good version forward and checks the recovered contents and all three retained versions. | Use the result to explain why copying the older version forward preserves evidence. The script uses dummy credentials in an emulator. |

### Reproduce the offline cases

From the repository root, run the following command with Python 3.10 or newer. The standard library is sufficient.

    python it-support-labs/support_cases.py

Compare the output with [the recorded results](sample-result.json). The [input records](fixtures.json) contain simulated sign-in events, two trunk snapshots per switch and the twelve support tickets. The JSON for the switch is a normalized fixture based on trunk status fields. It does not parse arbitrary IOS output.

On Windows, open PowerShell in the repository root and run the script below.

    & ./it-support-labs/windows-restore.ps1

For the AWS exercise, use a Python virtual environment and run:

    python -m pip install 'moto[s3]>=5,<6' 'boto3>=1.35,<2'
    python it-support-labs/s3_restore.py

[Open verification runs](https://github.com/rehmannadeem/rehmannadeem/actions/workflows/support-portfolio.yml) for the Linux and Windows checks. A green run is evidence about the tested software and fixtures. Entra tenant administration, work on physical switches and production AWS operations require separate operational evidence.

### Where AI helps a real support desk

The queue report identifies the breached tickets. A technician can give a language model the redacted observations and ask it to draft two sentences for a customer. For example, “The editor signed in successfully on the later attempt. We’re reviewing the contractor’s blocked sign-in separately.” A support lead can verify that wording against the two records. It would be incorrect to promise that a policy was changed.

[MSP Service Desk V1](https://github.com/rehmannadeem/armans-msp-service-desk) is the separate AI-assisted support demonstration. It retrieves approved guidance, cites the source, sends routing through dispatcher approval and records escalation or resolution. These casebook scripts produce deterministic evidence. They do not send logs to an external model.

### Vendor documentation

[Microsoft Entra sign-in error codes](https://learn.microsoft.com/en-us/entra/identity-platform/reference-error-codes) · [Cisco VLAN trunks](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst3650/software/release/37e/consolidated_guide/configuration_guide/configuring_vlan_trunks.pdf) · [Restoring earlier S3 versions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RestoringPreviousVersions.html)
