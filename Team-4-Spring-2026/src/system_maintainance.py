class SystemMaintainer:
    def __init__(self, maintainer_id):
        self.maintainer_id = maintainer_id
        self.system_status = "online"
        self.issues_log = []

    def update_system(self, update_notes):
        if not update_notes:
            raise ValueError("Update notes cannot be empty.")
        return f"System updated by maintainer {self.maintainer_id}: {update_notes}"

    def resolve_issues(self, issue):
        if not issue:
            raise ValueError("Issue description cannot be empty.")
        self.issues_log.append({"issue": issue, "status": "resolved"})
        return f"Issue resolved: {issue}"

    def view_system_status(self):
        return {
            "maintainer_id": self.maintainer_id,
            "system_status": self.system_status,
            "open_issues": len([i for i in self.issues_log if i["status"] != "resolved"])
        }

    def __repr__(self):
        return f"SystemMaintainer(id={self.maintainer_id}, status={self.system_status})"