def get_profile(conf_dir, sender, recipients):
    return True


def encrypt_message(profile, data, sender, recipients, subject):
    data["To"] = ", ".join(recipients)
    data["From"] = sender
    data["Subject"] = subject
    data["Chat-Version"] = "1.0"
    return data
