#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  printf 'Usage: %s https://<cloudfront-domain>\n' "$0" >&2
  exit 2
fi

base_url="${1%/}"
if [[ "$base_url" != https://* ]]; then
  printf 'Error: provide the HTTPS CloudFront application URL.\n' >&2
  exit 2
fi

check_response() {
  local url="$1"
  local expected_status="$2"
  local expected_body="$3"
  local response_file
  local status

  response_file="$(mktemp)"
  trap 'rm -f "$response_file"' RETURN

  status="$(curl --silent --show-error --max-time 20 \
    --output "$response_file" --write-out '%{http_code}' "$url")"
  if [[ "$status" != "$expected_status" ]]; then
    printf 'FAIL %s expected HTTP %s, received HTTP %s\n' \
      "$url" "$expected_status" "$status" >&2
    return 1
  fi
  if ! grep -Fq "$expected_body" "$response_file"; then
    printf 'FAIL %s returned HTTP %s but did not contain the expected marker\n' \
      "$url" "$status" >&2
    return 1
  fi
  printf 'PASS %s returned HTTP %s with expected content\n' "$url" "$status"
}

printf 'Read-only smoke test started at %s UTC\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
check_response "$base_url/" 200 "Hello from the primary AWS region"
check_response "$base_url/origin-health" 200 "healthy"
printf 'NOTE This checks the primary response and health endpoint only; it does not trigger or prove failover.\n'
