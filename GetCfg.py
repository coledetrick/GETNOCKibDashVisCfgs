import requests
import json
import urllib3

# 🔇 Optional: silence the InsecureRequestWarning (since you're using verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KIBANA_BASE = "https://janus-kibana.cv000-telematics.net/_plugin/kibana"
DASHBOARD_IDS = [
    "ccec0d90-d76a-11ec-9b3a-19d98a79547e",
]

VERIFY_SSL = False  # keep False if you're on corp self-signed certs


def kibana_get(path):
    url = f"{KIBANA_BASE}{path}"
    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json",
    }

    resp = requests.get(url, headers=headers, verify=VERIFY_SSL)

    # Helpful debug
    if resp.status_code != 200:
        print(f"\n--- ERROR {resp.status_code} for {url} ---")
        print(resp.text[:1000])  
        raise SystemExit(1)

    return resp.json()


def get_dashboard_visualizations(dashboard_id):
    print(f"\n### Fetching dashboard {dashboard_id}")
    dashboard = kibana_get(f"/api/saved_objects/dashboard/{dashboard_id}?pretty=true")

    panels = dashboard.get("references", [])
    vis_ids = [p["id"] for p in panels if p["type"] == "visualization"]

    print(f"Found {len(vis_ids)} visualizations on dashboard {dashboard_id}")

    vis_configs = []

    for vis_id in vis_ids:
        print(f" Fetching visualization {vis_id}")
        vis = kibana_get(f"/api/saved_objects/visualization/{vis_id}?pretty=true")

        entry = {
            "id": vis_id,
            "title": vis["attributes"].get("title"),
            "visState": json.loads(vis["attributes"].get("visState", "{}")),
            "searchSourceJSON": json.loads(
                vis["attributes"]["kibanaSavedObjectMeta"].get("searchSourceJSON", "{}")
            ),
        }

        vis_configs.append(entry)

    return vis_configs


def main():
    all_results = {}

    for dash_id in DASHBOARD_IDS:
        configs = get_dashboard_visualizations(dash_id)
        all_results[dash_id] = configs

    with open("dashboard_visualization_configs.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print("\n Completed. Saved to dashboard_visualization_configs.json")


if __name__ == "__main__":
    main()
