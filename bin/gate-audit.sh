#!/usr/bin/env bash
# ── THE COMPARE IN THE INTERVAL. A CODEOWNERS row and the tree it names are
# two records of one fact, each under its own edit process, and between
# judgements the pair states nothing: a fixed row restores agreement once,
# a standing judge keeps it. This is the judgement, sized for a stranger's
# CI: fetch the released binary at a pinned tag, check the bytes against
# the sha256 published beside them, and run both import mouths over the
# tree. A refusal is printed at its file:line, echoed as a GitHub
# annotation, and the exit code is the verdict.
#
# Held by tests/smoke.py: the pinned tag in action.yml is the VERSION the
# vein carries, the asset names here are the release road's own, and the
# three vectors (dead, clean, undeclared) run this file with the local
# binary standing in for the download. The download road itself is walked
# by the `action` job in CI against a published tag.
set -u
VER="${1:?release tag, like v0.2.2}"
TREE="${2:-.}"

# the refusals printed at an address, written on every way out, the early ones
# too, for a caller that must tell a judged red from any other red (the
# `action` job's negative control asks this): a red with none is not a verdict
REFUSED=0
trap 'if [ -n "${GITHUB_OUTPUT:-}" ]; then echo "refusals=$REFUSED" >> "$GITHUB_OUTPUT"; fi' EXIT

# the runner says what it is; off a runner, the machine does
OS="${RUNNER_OS:-}"; ARCH="${RUNNER_ARCH:-}"
if [ -z "$OS" ]; then
  case "$(uname -s)" in
    Darwin) OS=macOS ;; Linux) OS=Linux ;;
    MINGW*|MSYS*|CYGWIN*) OS=Windows ;; *) OS="$(uname -s)" ;;
  esac
fi
if [ -z "$ARCH" ]; then
  case "$(uname -m)" in
    arm64|aarch64) ARCH=ARM64 ;; x86_64|amd64) ARCH=X64 ;; *) ARCH="$(uname -m)" ;;
  esac
fi
case "$OS/$ARCH" in
  Linux/X64)     ASSET=gate-linux-x86_64 ;;
  Linux/ARM64)   ASSET=gate-linux-arm64 ;;
  macOS/ARM64)   ASSET=gate-macos-arm64 ;;
  Windows/X64)   ASSET=gate-windows-x86_64.exe ;;
  *) echo "gate's releases carry linux-x86_64, linux-arm64, macos-arm64, windows-x86_64," \
          "and this runner is $OS/$ARCH: build from the one source file instead, bin/build-cli.sh at $VER"
     exit 1 ;;
esac

if [ -n "${GATE_AUDIT_BIN:-}" ]; then
  BIN="$GATE_AUDIT_BIN"
else
  D="$(mktemp -d)"
  URL="https://github.com/DanielSwift1992/gate/releases/download/$VER/$ASSET"
  curl -fsSL -o "$D/$ASSET" "$URL" \
    || { echo "no $ASSET under the tag $VER: $URL answered nothing"; exit 1; }
  curl -fsSL -o "$D/$ASSET.sha256" "$URL.sha256" \
    || { echo "no sha256 beside $ASSET under the tag $VER"; exit 1; }
  # the hash names the artifact; the honest check is a rebuild, and the
  # README says that command
  if command -v sha256sum >/dev/null 2>&1; then SUM="sha256sum"; else SUM="shasum -a 256"; fi
  ( cd "$D" && $SUM -c "$ASSET.sha256" >/dev/null ) \
    || { echo "the bytes do not answer to the name the release printed beside them"; exit 1; }
  chmod +x "$D/$ASSET"
  BIN="$D/$ASSET"
fi

# ── A RED IS A VERDICT ONLY WHEN THE TOOL ANSWERED. On 19.10 the dead tree
# went red with no refusal at any address, the clean tree went red too, and
# the job's control took the first for the refusal it stands on. Where it
# broke is not known: no step said. So every answer is read as gate answers,
# an exit and a first line that go together, and anything else is said aloud
# as the tool not answering, with what it did print, and counts no refusal.
# The release's linux binary is built without the Swift runtime inside it,
# so whether it starts at all is the runner image's business: the version is
# asked first.
broke() {
  echo "::error::$1 did not answer as gate answers (exit $2): ${3:-it printed nothing}"
  RED=1
}
RED=0
START="$("$BIN" --version 2>&1)"; CODE=$?
FIRST="$(printf '%s\n' "$START" | head -1)"
case "$CODE/$FIRST" in
  "0/gate "*) ;;
  *) broke "$(basename "$BIN") --version at $VER" "$CODE" "$FIRST"; exit 1 ;;
esac

cd "$TREE" || { echo "no tree at $TREE"; exit 1; }

# a refusal line is `  file:line · claim`; say it again as an annotation
note() {
  printf '%s\n' "$1" | while IFS= read -r line; do
    case "$line" in
      "  "*" · "*)
        addr="${line#  }"; addr="${addr%% · *}"; msg="${line#*" · "}"
        f="${addr%:*}"; n="${addr##*:}"
        [ "$f" = "$addr" ] && continue
        case "$n" in ''|*[!0-9]*) continue ;; esac
        printf '::error file=%s,line=%s::%s\n' "$2$f" "$n" "$msg"
        ;;
    esac
  done
}

CO=""
for p in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS; do
  if [ -f "$p" ]; then CO="$p"; break; fi
done
if [ -n "$CO" ]; then
  OUT="$("$BIN" import codeowners --tree . 2>&1)"; CODE=$?
  printf '%s\n' "$OUT"
  case "$CODE/$OUT" in
    "1/import codeowners: refused "*)
      RED=1
      SAID="$(note "$OUT" "")"
      [ -n "$SAID" ] && printf '%s\n' "$SAID"
      REFUSED=$((REFUSED + $(printf '%s\n' "$SAID" | grep -c '^::error file=')))
      ;;
    "0/import codeowners: holds"*|"0/import codeowners: observed"*) ;;
    *) broke "import codeowners" "$CODE" "$(printf '%s\n' "$OUT" | head -1)" ;;
  esac
else
  echo "no CODEOWNERS file found (looked at CODEOWNERS, .github/CODEOWNERS," \
       "docs/CODEOWNERS): nothing to check on this half"
fi

# `observed` with nothing declared exits 1 at the mouth, because a person
# who asked to judge nothing deserves a refusal; a tree that declares no
# filter is not refused by an audit of what it declares. So `observed` is
# not red at either exit, `refused` is red, and anything else is the tool
# not answering.
OUT="$("$BIN" import workflows --tree . 2>&1)"; CODE=$?
printf '%s\n' "$OUT"
case "$CODE/$OUT" in
  "1/import workflows: refused "*)
    RED=1
    SAID="$(note "$OUT" ".github/workflows/")"
    [ -n "$SAID" ] && printf '%s\n' "$SAID"
    REFUSED=$((REFUSED + $(printf '%s\n' "$SAID" | grep -c '^::error file=')))
    ;;
  "0/import workflows: holds"*|"0/import workflows: observed"*|"1/import workflows: observed"*) ;;
  *) broke "import workflows" "$CODE" "$(printf '%s\n' "$OUT" | head -1)" ;;
esac

exit $RED
