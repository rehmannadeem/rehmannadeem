"""Offline, reproducible support cases. Run with Python 3.10+."""
import argparse
import json
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sign_in_cases(events):
    """Triage patterns in synthetic Microsoft Graph sign-in records."""
    guidance = {50076: "MFA required", 53003: "Conditional Access blocked access"}
    by_user = {}
    for event in sorted(events, key=lambda event: event["createdDateTime"]):
        code = event["status"]["errorCode"]
        user = event["userPrincipalName"]
        by_user.setdefault(user, []).append({
            "time": event["createdDateTime"], "application": event["appDisplayName"],
            "result": "Success" if code == 0 else guidance.get(code, "Further review required"),
            "code": code, "correlation": event["correlationId"]
        })
    return by_user


def allowed_vlans(text):
    """Expand an explicit, fixture-sized Cisco IOS VLAN allow list."""
    result = set()
    for token in text.split(","):
        ends = token.strip().split("-")
        if len(ends) not in (1, 2):
            raise ValueError(f"Invalid VLAN range: {token}")
        low, high = int(ends[0]), int(ends[-1])
        if not 1 <= low <= high <= 4094:
            raise ValueError(f"Invalid VLAN range: {token}")
        result.update(range(low, high + 1))
    return result


def trunk_path(switches, vlan):
    """Check both ends of one synthetic trunk and report each blocking stage."""
    issues = []
    for switch, fields in switches.items():
        if fields["mode"] != "trunking":
            issues.append(f"{switch}: link is not trunking")
        for stage in ("allowed", "active", "forwarding"):
            if vlan not in allowed_vlans(fields[stage]):
                issues.append(f"{switch}: VLAN {vlan} absent from {stage}")
    return {"vlan": vlan, "passes_snapshots": not issues, "issues": issues}


def queue_report(tickets):
    """Calculate queue and SLA figures from fictional closed/open tickets."""
    db = sqlite3.connect(":memory:")
    try:
        db.execute("CREATE TABLE tickets (id TEXT PRIMARY KEY, team TEXT, elapsed INTEGER, target INTEGER)")
        db.executemany("INSERT INTO tickets VALUES (?,?,?,?)", tickets)
        sql = """
            SELECT team, COUNT(*) AS tickets, COUNT(elapsed) AS closed,
                   SUM(CASE WHEN elapsed IS NULL THEN 1 ELSE 0 END) AS open,
                   SUM(CASE WHEN elapsed > target THEN 1 ELSE 0 END) AS breached
            FROM tickets GROUP BY team ORDER BY team
        """
        cursor = db.execute(sql)
        fields = [d[0] for d in cursor.description]
        return [dict(zip(fields, row)) for row in cursor.fetchall()]
    finally:
        db.close()


def run():
    cases = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))
    network = {period: [trunk_path(ports, vlan) for vlan in (20, 10, 99)]
               for period, ports in cases["trunk"].items()}
    identity = sign_in_cases(cases["sign_ins"])
    queue = queue_report(cases["tickets"])
    assert [[r["passes_snapshots"] for r in network[k]] for k in ("before", "after")] == [
        [False, True, False], [True, True, False]]
    assert [r["code"] for r in identity["editor@example.test"]] == [50076, 0]
    assert identity["contractor@example.test"][-1]["code"] == 53003
    assert identity["reviewer@example.test"][-1]["result"] == "Further review required"
    assert sum(row["closed"] for row in queue) == 8
    assert sum(row["open"] for row in queue) == 4
    assert sum(row["breached"] for row in queue) == 2
    return {"sign_in_triage": identity, "trunk_validation": network, "ticket_report": queue}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", type=Path, help="Optional JSON destination")
    args = cli.parse_args()
    output = json.dumps(run(), indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
