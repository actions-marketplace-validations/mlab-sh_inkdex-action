# inkdex-action

Scan a repository with [inkdex](https://inkdex.mlab.sh) in GitHub Actions: injections (flows
from a request to a sink), secrets, weak crypto, dangerous settings, GitHub workflows and
vulnerable dependencies. Findings go to the repository's **Security › Code scanning** and to pull
requests.

```yaml
name: inkdex
on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write          # code scanning upload
    steps:
      - uses: actions/checkout@v4
      - uses: mlab-sh/inkdex-action@v1
        with:
          token: ${{ secrets.INKDEX_TOKEN }}
          fail-on: high
```

`INKDEX_TOKEN` is an inkdex CI token (see [License](https://inkdex.mlab.sh/docs/inkdex/getting-started/license)).
The action installs inkdex from apt.mlab.sh, so it runs on Ubuntu / Debian runners; on others,
install inkdex before it.

## Who sees the findings

Public repositories included:

- **Not in the logs.** The scan writes its report to a file (`sarif`); the job's log, public on
  a public repository, only says how many findings there are.
- **Code scanning alerts** (Security › Code scanning) are readable by the repository's
  maintainers (write access), not by visitors. Only high and critical findings go there by
  default (`upload-severity`): medium and low ones stay in the report file.
- **Not as an artifact.** The action uploads none: on a public repository anyone signed in to
  GitHub can download a run's artifacts. Do not add an `upload-artifact` of the report there.
- **Pull requests.** Code scanning annotates the lines a pull request changes, and anyone who can
  read the pull request sees those annotations. On a public repository, run with
  `upload-sarif: "false"` on `pull_request` if new findings must not show there before a fix.
- **Forks.** A pull request from a fork gets neither your secrets nor `security-events: write`:
  run the job on pushes and on your own branches' pull requests.

## Inputs

| Input | Default | |
|---|---|---|
| `token` | (required) | The inkdex CI token. |
| `fail-on` | none | Fail the job on a finding at least this severe: `critical`, `high`, `medium`, `low`. |
| `since` | none | Only the findings absent at this revision (needs `fetch-depth: 0`). |
| `sarif` | `inkdex.sarif` | Where the report is written. |
| `upload-sarif` | `true` | Upload it to code scanning. |
| `upload-severity` | `high` | The least severe findings code scanning gets (`critical`, `high`, `medium`, `low`); the report file keeps all. |
| `cache` | `actions` | Keep the index between runs: `actions` (GitHub's cache), `none`, or `s3://bucket/key`. |
| `args` | none | More arguments for `inkdex-vuln scan` (`--path src/**`, `--explain`…). |

Outputs: `sarif` (the report's path) and `exit-code` (0: nothing at the threshold, 1: findings at
it, 2: inkdex could not run).

## Only what a pull request adds

```yaml
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: mlab-sh/inkdex-action@v1
        with:
          token: ${{ secrets.INKDEX_TOKEN }}
          since: ${{ github.event.pull_request.base.sha }}
          fail-on: high
```

## The index in a bucket

With `cache: s3://bucket/key`, every run starts from the index the default branch pushed there
(other branches, pull requests, other workflows), and only pushes to the default branch write
it: a pull request, from a fork above all, never does. The bucket is read with the AWS CLI's
variables (AWS S3, Cloudflare R2, MinIO…):

```yaml
      - uses: mlab-sh/inkdex-action@v1
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.INKDEX_S3_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.INKDEX_S3_SECRET }}
          AWS_REGION: auto
          AWS_ENDPOINT_URL: https://<account>.r2.cloudflarestorage.com
        with:
          token: ${{ secrets.INKDEX_TOKEN }}
          cache: s3://my-bucket/inkdex/main.pack
```

## Versions

`v1` follows the latest `v1.x.y`. Pin a full commit SHA if your policy asks for it.

Releasing (maintainers): push a `vX.Y.Z` tag; the `release` workflow moves `vX` onto it and
creates the GitHub release.
Documentation: https://inkdex.mlab.sh
