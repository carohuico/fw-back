class DefaultExceptionsCode:
    DE001 = "Failed to login! User unauthorised!"
    DE002 = "Failed to login! Invalid authentication code"
    DE003 = "Password expired! please reset the password"
    DEIP = "Failed to login! Incorrect Password!"
    DEIL = "Invalid login! Please contact administrator"


class MFAConfiguration:
    MFA001 = "Your Organization Admin has requested you to setup the multi-factor authentication within next {} days."
    MFA002 = "Your Organization Admin has requested you to setup the multi-factor authentication within a day."
    MFA003 = "Your Organization Admin has requested you to setup the multi-factor authentication."


class UserAccessExceptions:
    UAE = "User doesn't have the access"

class ValidationExceptions:
    IL001 = "Error Code IL001: Required Keys are missing!"
    IL002 = "Error Code IL002: User id is missing in the cookies!"

class userExceptions:
    UID_UN_NOT_EMPTY = "Both user_id and user_name cannot be empty"
    FAILED_TO_SAVE = "Failed to save the user details"
    USER_INACTIVE = "User Inactive, please contact administrator"
    INCORRECT_USERID = "Failed. Incorrect user id or user id doesn’t exist. Please try again."
    USER_NOT_EXIST = "User does not Exists"




