##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    from atproto_client import models

ReasonType = t.Union[
    'models.ToolsOzoneReportDefs.ReasonAppeal',
    'models.ToolsOzoneReportDefs.ReasonViolenceAnimalWelfare',
    'models.ToolsOzoneReportDefs.ReasonViolenceThreats',
    'models.ToolsOzoneReportDefs.ReasonViolenceGraphicContent',
    'models.ToolsOzoneReportDefs.ReasonViolenceSelfHarm',
    'models.ToolsOzoneReportDefs.ReasonViolenceGlorification',
    'models.ToolsOzoneReportDefs.ReasonViolenceExtremistContent',
    'models.ToolsOzoneReportDefs.ReasonViolenceTrafficking',
    'models.ToolsOzoneReportDefs.ReasonViolenceOther',
    'models.ToolsOzoneReportDefs.ReasonSexualAbuseContent',
    'models.ToolsOzoneReportDefs.ReasonSexualNCII',
    'models.ToolsOzoneReportDefs.ReasonSexualSextortion',
    'models.ToolsOzoneReportDefs.ReasonSexualDeepfake',
    'models.ToolsOzoneReportDefs.ReasonSexualAnimal',
    'models.ToolsOzoneReportDefs.ReasonSexualUnlabeled',
    'models.ToolsOzoneReportDefs.ReasonSexualOther',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyCSAM',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyGroom',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyMinorPrivacy',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyEndangerment',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyHarassment',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyPromotion',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyOther',
    'models.ToolsOzoneReportDefs.ReasonHarassmentTroll',
    'models.ToolsOzoneReportDefs.ReasonHarassmentTargeted',
    'models.ToolsOzoneReportDefs.ReasonHarassmentHateSpeech',
    'models.ToolsOzoneReportDefs.ReasonHarassmentDoxxing',
    'models.ToolsOzoneReportDefs.ReasonHarassmentOther',
    'models.ToolsOzoneReportDefs.ReasonMisleadingBot',
    'models.ToolsOzoneReportDefs.ReasonMisleadingImpersonation',
    'models.ToolsOzoneReportDefs.ReasonMisleadingSpam',
    'models.ToolsOzoneReportDefs.ReasonMisleadingScam',
    'models.ToolsOzoneReportDefs.ReasonMisleadingSyntheticContent',
    'models.ToolsOzoneReportDefs.ReasonMisleadingMisinformation',
    'models.ToolsOzoneReportDefs.ReasonMisleadingOther',
    'models.ToolsOzoneReportDefs.ReasonRuleSiteSecurity',
    'models.ToolsOzoneReportDefs.ReasonRuleStolenContent',
    'models.ToolsOzoneReportDefs.ReasonRuleProhibitedSales',
    'models.ToolsOzoneReportDefs.ReasonRuleBanEvasion',
    'models.ToolsOzoneReportDefs.ReasonRuleOther',
    'models.ToolsOzoneReportDefs.ReasonCivicElectoralProcess',
    'models.ToolsOzoneReportDefs.ReasonCivicDisclosure',
    'models.ToolsOzoneReportDefs.ReasonCivicInterference',
    'models.ToolsOzoneReportDefs.ReasonCivicMisinformation',
    'models.ToolsOzoneReportDefs.ReasonCivicImpersonation',
    str,
]  #: Reason type

ReasonAppeal = t.Literal['tools.ozone.report.defs#reasonAppeal']  #: Appeal a previously taken moderation action

ReasonViolenceAnimalWelfare = t.Literal[
    'tools.ozone.report.defs#reasonViolenceAnimalWelfare'
]  #: Animal welfare violations

ReasonViolenceThreats = t.Literal['tools.ozone.report.defs#reasonViolenceThreats']  #: Threats or incitement

ReasonViolenceGraphicContent = t.Literal[
    'tools.ozone.report.defs#reasonViolenceGraphicContent'
]  #: Graphic violent content

ReasonViolenceSelfHarm = t.Literal['tools.ozone.report.defs#reasonViolenceSelfHarm']  #: Self harm

ReasonViolenceGlorification = t.Literal[
    'tools.ozone.report.defs#reasonViolenceGlorification'
]  #: Glorification of violence

ReasonViolenceExtremistContent = t.Literal[
    'tools.ozone.report.defs#reasonViolenceExtremistContent'
]  #: Extremist content. These reports will be sent only be sent to the application's Moderation Authority.

ReasonViolenceTrafficking = t.Literal['tools.ozone.report.defs#reasonViolenceTrafficking']  #: Human trafficking

ReasonViolenceOther = t.Literal['tools.ozone.report.defs#reasonViolenceOther']  #: Other violent content

ReasonSexualAbuseContent = t.Literal['tools.ozone.report.defs#reasonSexualAbuseContent']  #: Adult sexual abuse content

ReasonSexualNCII = t.Literal['tools.ozone.report.defs#reasonSexualNCII']  #: Non-consensual intimate imagery

ReasonSexualSextortion = t.Literal['tools.ozone.report.defs#reasonSexualSextortion']  #: Sextortion

ReasonSexualDeepfake = t.Literal['tools.ozone.report.defs#reasonSexualDeepfake']  #: Deepfake adult content

ReasonSexualAnimal = t.Literal['tools.ozone.report.defs#reasonSexualAnimal']  #: Animal sexual abuse

ReasonSexualUnlabeled = t.Literal['tools.ozone.report.defs#reasonSexualUnlabeled']  #: Unlabelled adult content

ReasonSexualOther = t.Literal['tools.ozone.report.defs#reasonSexualOther']  #: Other sexual violence content

ReasonChildSafetyCSAM = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyCSAM'
]  #: Child sexual abuse material (CSAM). These reports will be sent only be sent to the application's Moderation Authority.

ReasonChildSafetyGroom = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyGroom'
]  #: Grooming or predatory behavior. These reports will be sent only be sent to the application's Moderation Authority.

ReasonChildSafetyMinorPrivacy = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyMinorPrivacy'
]  #: Privacy violation involving a minor

ReasonChildSafetyEndangerment = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyEndangerment'
]  #: Child endangerment. These reports will be sent only be sent to the application's Moderation Authority.

ReasonChildSafetyHarassment = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyHarassment'
]  #: Harassment or bullying of minors

ReasonChildSafetyPromotion = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyPromotion'
]  #: Promotion of child exploitation. These reports will be sent only be sent to the application's Moderation Authority.

ReasonChildSafetyOther = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyOther'
]  #: Other child safety. These reports will be sent only be sent to the application's Moderation Authority.

ReasonHarassmentTroll = t.Literal['tools.ozone.report.defs#reasonHarassmentTroll']  #: Trolling

ReasonHarassmentTargeted = t.Literal['tools.ozone.report.defs#reasonHarassmentTargeted']  #: Targeted harassment

ReasonHarassmentHateSpeech = t.Literal['tools.ozone.report.defs#reasonHarassmentHateSpeech']  #: Hate speech

ReasonHarassmentDoxxing = t.Literal['tools.ozone.report.defs#reasonHarassmentDoxxing']  #: Doxxing

ReasonHarassmentOther = t.Literal[
    'tools.ozone.report.defs#reasonHarassmentOther'
]  #: Other harassing or hateful content

ReasonMisleadingBot = t.Literal['tools.ozone.report.defs#reasonMisleadingBot']  #: Fake account or bot

ReasonMisleadingImpersonation = t.Literal['tools.ozone.report.defs#reasonMisleadingImpersonation']  #: Impersonation

ReasonMisleadingSpam = t.Literal['tools.ozone.report.defs#reasonMisleadingSpam']  #: Spam

ReasonMisleadingScam = t.Literal['tools.ozone.report.defs#reasonMisleadingScam']  #: Scam

ReasonMisleadingSyntheticContent = t.Literal[
    'tools.ozone.report.defs#reasonMisleadingSyntheticContent'
]  #: Unlabelled gen-AI or synthetic content

ReasonMisleadingMisinformation = t.Literal[
    'tools.ozone.report.defs#reasonMisleadingMisinformation'
]  #: Harmful false claims

ReasonMisleadingOther = t.Literal['tools.ozone.report.defs#reasonMisleadingOther']  #: Other misleading content

ReasonRuleSiteSecurity = t.Literal['tools.ozone.report.defs#reasonRuleSiteSecurity']  #: Hacking or system attacks

ReasonRuleStolenContent = t.Literal['tools.ozone.report.defs#reasonRuleStolenContent']  #: Stolen content

ReasonRuleProhibitedSales = t.Literal[
    'tools.ozone.report.defs#reasonRuleProhibitedSales'
]  #: Promoting or selling prohibited items or services

ReasonRuleBanEvasion = t.Literal['tools.ozone.report.defs#reasonRuleBanEvasion']  #: Banned user returning

ReasonRuleOther = t.Literal['tools.ozone.report.defs#reasonRuleOther']  #: Other

ReasonCivicElectoralProcess = t.Literal[
    'tools.ozone.report.defs#reasonCivicElectoralProcess'
]  #: Electoral process violations

ReasonCivicDisclosure = t.Literal[
    'tools.ozone.report.defs#reasonCivicDisclosure'
]  #: Disclosure & transparency violations

ReasonCivicInterference = t.Literal[
    'tools.ozone.report.defs#reasonCivicInterference'
]  #: Voter intimidation or interference

ReasonCivicMisinformation = t.Literal['tools.ozone.report.defs#reasonCivicMisinformation']  #: Election misinformation

ReasonCivicImpersonation = t.Literal[
    'tools.ozone.report.defs#reasonCivicImpersonation'
]  #: Impersonation of electoral officials/entities
