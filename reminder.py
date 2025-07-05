import argparse
import logging
import os
import random
import sys
import time
import yaml
from plyer import notification

def load_config(path):
    if not os.path.exists(path):
        logging.error("Config file not found: %s", path)
        sys.exit(1)
    with open(path, "r") as f:
        return yaml.safe_load(f)

def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )
    logging.info("Sent notification: %r", message)

def main():
    parser = argparse.ArgumentParser(
        description="Stretch reminders with an optional shuffle")
    parser.add_argument(
        "-c", "--config", default="config.yaml",
        help="Path to YAML config file")
    parser.add_argument(
        "--no-notify", action="store_true",
        help="Print messages instead of desktop notifications")
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S")

    cfg = load_config(args.config)
    interval = cfg.get("interval_minutes", 30) * 60
    messages = cfg.get("messages", [])
    if not messages:
        logging.error("No messages defined!")
        sys.exit(1)

    shuffle = cfg.get("shuffle", False)
    no_repeat = cfg.get("no_repeat", False)
    cycle_once = cfg.get("cycle_once", False)

    last_msg = None
    index = 0

    pool = []
    if cycle_once:
        pool = list(messages)
        random.shuffle(pool)

    try:
        while True:
            if cycle_once:
                if not pool:
                    pool = list(messages)
                    random.shuffle(pool)
                msg = pool.pop(0)

            elif shuffle:
                if no_repeat and last_msg is not None:
                    msg = last_msg
                    while msg == last_msg:
                        msg = random.choice(messages)
                else:
                    msg = random.choice(messages)

            else:
                msg = messages[index % len(messages)]
                index += 1

            last_msg = msg

            if args.no_notify:
                print(f"[DRY] {msg}")
            else:
                send_notification("Stretch Reminder", msg)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("Stretch reminder stopped!")

if __name__ == "__main__":
    main()
