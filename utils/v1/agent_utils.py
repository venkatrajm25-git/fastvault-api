import os
import glob
import time
from datetime import datetime
import json
from typing import List


def write_agent_logs(log_dir: str, log_entries: List[str], json_log_data: List[dict]):
    """
    Prepends deduplication log entries to .log and .json log files with timestamps.
    Ensures newest logs appear at the top.
    """

    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add timestamp to each log entry (text)
    stamped_log_entries = [f"[{timestamp}] {entry}" for entry in log_entries]

    # 📄 Handle .txt file (prepend logs)
    txt_path = os.path.join(log_dir, "deduplication_log.log")
    existing_txt = ""
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            existing_txt = f.read()

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(stamped_log_entries) + "\n" + existing_txt)

    # Add timestamp to each JSON log entry
    for entry in json_log_data:
        entry["timestamp"] = timestamp

    # 📄 Handle .json file (prepend logs)
    json_log_path = os.path.join(log_dir, "deduplication_log.json")
    existing_json_data = []

    if os.path.exists(json_log_path):
        with open(json_log_path, "r", encoding="utf-8") as jf:
            try:
                existing_json_data = json.load(jf)
            except json.JSONDecodeError:
                pass

    with open(json_log_path, "w", encoding="utf-8") as jf:
        json.dump(json_log_data + existing_json_data, jf, indent=4)


def delete_old_agent_logs(
    log_dir: str, pattern: str = "deduplication_log_*", days: int = 7
):
    """
    Deletes log files in the given directory older than the specified number of days.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_files = glob.glob(os.path.join(log_dir, f"{pattern}.log")) + glob.glob(
        os.path.join(log_dir, f"{pattern}.json")
    )
    now = time.time()
    for file in log_files:
        if os.stat(file).st_mtime < now - days * 86400:
            os.remove(file)


# def write_agent_using_llm_logs(
#     log_dir: str, log_entries: List[str], json_log_data: List[dict]
# ):
#     """
#     Prepends deduplication log entries to .log and .json log files with timestamps.
#     Ensures newest logs appear at the top.
#     """

#     os.makedirs(log_dir, exist_ok=True)
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     # Add timestamp to each log entry (text)
#     stamped_log_entries = [f"[{timestamp}] {entry}" for entry in log_entries]

#     # 📄 Handle .txt file (prepend logs)
#     txt_path = os.path.join(log_dir, "deduplication_log_llm.log")
#     existing_txt = ""
#     if os.path.exists(txt_path):
#         with open(txt_path, "r", encoding="utf-8") as f:
#             existing_txt = f.read()

#     with open(txt_path, "w", encoding="utf-8") as f:
#         f.write("\n".join(stamped_log_entries) + "\n" + existing_txt)

#     # Add timestamp to each JSON log entry
#     for entry in json_log_data:
#         entry["timestamp"] = timestamp

#     # 📄 Handle .json file (prepend logs)
#     json_log_path = os.path.join(log_dir, "deduplication_log_llm.json")
#     existing_json_data = []

#     if os.path.exists(json_log_path):
#         with open(json_log_path, "r", encoding="utf-8") as jf:
#             try:
#                 existing_json_data = json.load(jf)
#             except json.JSONDecodeError:
#                 pass

#     with open(json_log_path, "w", encoding="utf-8") as jf:
#         json.dump(json_log_data + existing_json_data, jf, indent=4)
