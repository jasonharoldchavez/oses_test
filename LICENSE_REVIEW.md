# License review — release blocker

Status: review required. This file does not grant or change a license.

The current `LICENSE.txt` combines Apache License 2.0 wording with a separate restrictive commercial software agreement. The README also references license filenames that are not present on the default branch. Combining two different sets of terms in one file can leave users uncertain which rights apply and may create inconsistent packaging/metadata.

Do not treat this note as resolving the conflict. Before release or commercial distribution:
1. Decide, with qualified legal advice if needed, whether the project is Apache-2.0 only, dual-licensed, or offered under another model.
2. If dual-licensing is intended, make the grants and scope explicit and separate the license texts; do not imply that commercial permission is required for rights already granted under Apache-2.0.
3. Make `pyproject.toml`, README, source distribution, wheel metadata, and all license/notices agree.
4. Verify ownership and provenance of all contributed and third-party code.
5. Build and inspect wheel and sdist metadata before publishing.

Technical note: Streaming Guardian's benchmark results are synthetic unless explicitly stated otherwise. Passing tests is not proof of field reliability or a calibrated detector.
