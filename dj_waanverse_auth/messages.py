from typing import TypedDict

from django.utils.translation import gettext_lazy as _


class MessagesSchema(TypedDict):
    status_unverified: str
    status_verified: str
    email_sent: str
    email_required: str
    mfa_enabled_success: str
    mfa_already_activated: str
    mfa_invalid_otp: str
    mfa_not_activated: str
    mfa_deactivated: str
    mfa_login_failed: str
    mfa_login_success: str
    invalid_account: str
    no_account: str
    password_reset_code_sent: str
    password_reset_successful: str
    already_authenticated: str
    logout_successful: str
    mfa_required: str
    mfa_recovery_codes_generated: str
    mfa_setup_failed: str
    recovery_codes_regeneration_error: str
    token_error: str
    general_msg: str
    mfa_code_generated_email_subject: str
    email_already_verified: str
    no_credentials: str
    user_creation_error: str
    attempts_limit: str
    invalid_password: str
    mfa_deactivated_email_subject: str
    reset_password_email_subject: str
    invalid_code: str
    expired_code: str
    email_exists: str
    password_mismatch: str
    verify_email_subject: str
    login_email_subject: str


class Messages(MessagesSchema):
    status_unverified = _("Your email remains unverified. Please verify it to proceed.")
    status_verified = _("Your email has been successfully verified.")
    no_account = _("No active account found.")
    email_sent = _("A verification email has been dispatched to your email address.")
    email_required = _("A valid email address is required to continue.")
    mfa_enabled_success = _(
        "Multi-factor authentication has been successfully enabled."
    )
    mfa_already_activated = _("Multi-factor authentication is already activated.")
    mfa_invalid_otp = _("The provided OTP is invalid. Please try again.")
    mfa_not_activated = _(
        "Multi-factor authentication is not activated for this account."
    )
    mfa_deactivated = _(
        "Multi-factor authentication has been successfully deactivated."
    )
    mfa_login_failed = _("MFA login failed due to an invalid OTP or recovery code.")
    mfa_login_success = _("MFA login was successful.")
    invalid_account = _("The provided account details are invalid. Please try again.")
    password_reset_code_sent = _(
        "A password reset code has been sent to your email address."
    )
    password_reset_successful = _("Your password has been reset successfully.")
    already_authenticated = _("You are already authenticated.")
    logout_successful = _("You have successfully logged out.")
    mfa_required = _("Multi-factor authentication is required for this action.")
    mfa_recovery_codes_generated = _(
        "New MFA recovery codes have been successfully generated."
    )
    mfa_setup_failed = _(
        "An error occurred during the setup of multi-factor authentication."
    )
    recovery_codes_regeneration_error = _(
        "An error occurred while generating recovery codes. Please try again."
    )
    token_error = _("An error occurred while processing the token. Please try again.")
    general_msg = _("An error occurred. Please try again later.")
    mfa_code_generated_email_subject = _(
        "New Multi-factor Authentication Recovery Codes Generated"
    )
    email_already_verified = _("Your email is already verified.")
    no_credentials = _("No valid credentials provided. Please check and try again.")
    user_creation_error = _("An error occurred during user creation. Please try again.")
    attempts_limit = _("Too many attempts. Please try again after the cooldown period.")
    invalid_password = _("The password provided is invalid.")
    mfa_deactivated_email_subject = _(
        "Multi-factor Authentication Deactivation Confirmation"
    )
    reset_password_email_subject = _("Password Reset Request")
    invalid_code = _("The provided code is invalid. Please try again.")
    email_exists = _("An account with this email already exists.")
    password_mismatch = _("The provided passwords do not match. Please try again.")
    verify_email_subject = _("Verify your email address")
    login_email_subject = _("New login alert")
    expired_code = _("The provided code has expired. Please try again.")
