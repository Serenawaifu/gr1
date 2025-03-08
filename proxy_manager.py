class ProxyManager:
    def __init__(self, db):
        self.db = db

    def load_proxies_from_file(self, file_path, user_id):
        with open(file_path, "r") as f:
            lines = f.read().splitlines()
            current_proxy = None
            for line in lines:
                if line.strip() == "":  # Skip empty lines
                    continue
                if "@" in line:  # Proxy line
                    parts = line.split("://")
                    protocol = parts[0]
                    auth, rest = parts[1].split("@")
                    user, password = auth.split(":")
                    ip, port = rest.split(":")
                    self.db.conn.execute("""
                        INSERT INTO proxies (
                            telegram_id, protocol, user, password, ip, port
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, protocol, user, password, ip, port))
                else:  # Account line (email:password or email:ref:password)
                    current_proxy = line
