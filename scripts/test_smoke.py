#!/usr/bin/env python3
"""Smoke test: run every CLI command, verify non-crash + non-empty output."""
import subprocess, sys, os, json

HOME = os.path.expanduser("~")
CLI = os.path.join(HOME, ".opencode", "scripts", "novahiz-cli.py")
PASS = 0
FAIL = 0

def run(label, cmd, expect_json=False, check_stdout=True, allow_exit=None):
    global PASS, FAIL
    try:
        r = subprocess.run([sys.executable, "-X", "utf8", CLI] + cmd, capture_output=True, text=True, timeout=30)
        ok = r.returncode == 0
        if allow_exit is not None and r.returncode in allow_exit:
            ok = True
        stdout = r.stdout or ""
        stderr = r.stderr or ""
        if expect_json and stdout.strip():
            try:
                json.loads(stdout)
            except json.JSONDecodeError:
                print(f"  FAIL {label}: stdout not valid JSON")
                ok = False
        if check_stdout and not stdout.strip() and not stderr.strip():
            print(f"  FAIL {label}: no output")
            ok = False
        if ok:
            print(f"  OK   {label}")
            PASS += 1
        else:
            detail = (stderr.strip() or stdout.strip() or "?")[:60]
            print(f"  FAIL {label} (exit={r.returncode}): {detail}")
            FAIL += 1
    except subprocess.TimeoutExpired:
        print(f"  FAIL {label}: timed out")
        FAIL += 1
    except Exception as e:
        print(f"  FAIL {label}: {e}")
        FAIL += 1

def main():
    global PASS, FAIL
    print(f"Smoke Test: novahiz-cli.py")
    print(f"{'='*50}")

    run("status", ["status"])
    run("health", ["health"])
    run("agents", ["agents"])
    run("skills", ["skills"])
    run("route", ["route", "security audit"])
    run("route nomatch", ["route", "zzzunknown"])
    run("search", ["search", "security"])
    run("model", ["model"])
    run("model resolve", ["model", "security", "audit"])
    run("model set invalid", ["model", "set", "invalid"])
    run("model history", ["model", "history"])
    run("ntm", ["ntm"])
    run("ntm clean", ["ntm", "clean"])
    run("logs", ["logs", "-n", "5"])
    run("debug", ["debug"])
    run("help", ["help"])

    print()
    print(f"{'='*50}")
    run("--json status", ["--json", "status"], expect_json=True)
    run("--json health", ["--json", "health"], expect_json=True)
    run("--json agents", ["--json", "agents"], expect_json=True)
    run("--json skills", ["--json", "skills"], expect_json=True)
    run("--json route", ["--json", "route", "api"], expect_json=True)
    run("--json search", ["--json", "search", "neo"], expect_json=True)
    run("--json model", ["--json", "model"], expect_json=True)
    run("--json model resolve", ["--json", "model", "security", "audit"], expect_json=True)
    run("--json ntm", ["--json", "ntm"], expect_json=True)
    run("--json logs", ["--json", "logs", "-n", "3"], expect_json=True)
    run("--json debug", ["--json", "debug"], expect_json=True)
    run("--json fallback", ["--json", "zzz"], expect_json=True, allow_exit={0, 2})

    print()
    print(f"{'='*50}")
    print(f"Results: {PASS} passed, {FAIL} failed out of {PASS+FAIL} tests")
    return 1 if FAIL else 0

if __name__ == "__main__":
    sys.exit(main())
